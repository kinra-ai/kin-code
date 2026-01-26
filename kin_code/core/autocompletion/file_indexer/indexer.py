"""High-performance file system indexer with incremental updates.

This module provides a thread-safe file system indexer that builds and maintains
an in-memory index of files and directories for fast autocompletion. It supports
incremental updates via file system watching, handles concurrent access with fine-
grained locking, and manages background rebuilds when switching between projects.

The indexer uses a multi-threaded architecture with coordinated cancellation to
ensure only one rebuild runs per root directory at a time. File system watches
provide efficient incremental updates, and ignore rules (gitignore-style) reduce
index size by excluding build artifacts, dependencies, and other irrelevant files.

Key components:
    - FileIndexer: Main indexer class with thread-safe access
    - FileIndexStore: In-memory storage with snapshot support
    - WatchController: File system watcher for incremental updates
    - IgnoreRules: Gitignore-style filtering
    - IndexEntry: Immutable file/directory metadata

Features:
    - Thread-safe concurrent access with RLock coordination
    - Background rebuilds in dedicated thread pool
    - Automatic rebuild cancellation on root directory changes
    - Incremental updates via file system watching
    - Mass change detection to trigger full rebuilds
    - Snapshot-based access for consistent reads during updates
    - Graceful shutdown with cleanup on exit

Threading model:
    - Main thread: Triggers rebuilds and retrieves snapshots
    - Rebuild thread: Scans file system and builds index
    - Watcher thread: Monitors file system changes
    - Locks coordinate access between threads

Typical usage:
    indexer = FileIndexer(mass_change_threshold=200)

    # Get index for current directory
    entries = indexer.get_index(Path.cwd())

    # Index is cached and auto-updated via file watching
    # Access again for instant results
    entries = indexer.get_index(Path.cwd())

    # Switch to different directory triggers rebuild
    entries = indexer.get_index(Path("/other/project"))

    # Stats for debugging/monitoring
    print(f"Total files: {indexer.stats.total_files}")
    print(f"Ignored files: {indexer.stats.ignored_files}")

Performance:
    The indexer is optimized for large repositories with tens of thousands of
    files. Background rebuilds prevent blocking the main thread, and file system
    watching avoids full rescans on small changes. The mass_change_threshold
    parameter triggers full rebuilds when many files change simultaneously (e.g.,
    git checkout).

Lifecycle:
    - First get_index() call triggers background rebuild and blocks until complete
    - Subsequent calls return cached snapshot instantly
    - File system changes apply incremental updates without blocking
    - Root directory change cancels pending rebuilds and starts new one
    - atexit handler ensures clean shutdown
"""

from __future__ import annotations

import atexit
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Event, RLock

from kin_code.core.autocompletion.file_indexer.ignore_rules import IgnoreRules
from kin_code.core.autocompletion.file_indexer.store import (
    FileIndexStats,
    FileIndexStore,
    IndexEntry,
)
from kin_code.core.autocompletion.file_indexer.watcher import Change, WatchController


@dataclass(slots=True)
class _RebuildTask:
    cancel_event: Event
    done_event: Event


class FileIndexer:
    def __init__(self, mass_change_threshold: int = 200) -> None:
        self._lock = RLock()  # guards _store snapshot access and watcher callbacks.
        self._stats = FileIndexStats()
        self._ignore_rules = IgnoreRules()
        self._store = FileIndexStore(
            self._ignore_rules, self._stats, mass_change_threshold=mass_change_threshold
        )
        self._watcher = WatchController(self._handle_watch_changes)
        self._rebuild_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="file-indexer"
        )
        self._active_rebuilds: dict[Path, _RebuildTask] = {}
        self._rebuild_lock = (
            RLock()
        )  # coordinates updates to _active_rebuilds and _target_root.
        self._target_root: Path | None = None
        self._shutdown = False

        atexit.register(self.shutdown)

    @property
    def stats(self) -> FileIndexStats:
        return self._stats

    def get_index(self, root: Path) -> list[IndexEntry]:
        resolved_root = root.resolve()

        with self._lock:  # read current root without blocking rebuild bookkeeping
            root_changed = (
                self._store.root is not None and self._store.root != resolved_root
            )

        if root_changed:
            self._watcher.stop()
            with self._rebuild_lock:  # cancel rebuilds targeting other roots
                self._target_root = resolved_root
                for other_root, task in self._active_rebuilds.items():
                    if other_root != resolved_root:
                        task.cancel_event.set()
                        task.done_event.set()
                        self._active_rebuilds.pop(other_root, None)

        with self._lock:
            needs_rebuild = self._store.root != resolved_root

        if needs_rebuild:
            with self._rebuild_lock:
                self._target_root = resolved_root
            self._start_background_rebuild(resolved_root)
            self._wait_for_rebuild(resolved_root)

        self._watcher.start(resolved_root)

        with self._lock:  # ensure root reference is fresh before snapshotting
            return self._store.snapshot()

    def refresh(self) -> None:
        self._watcher.stop()
        with self._rebuild_lock:
            for task in self._active_rebuilds.values():
                task.cancel_event.set()
                task.done_event.set()
            self._active_rebuilds.clear()
            self._target_root = None
        with self._lock:
            self._store.clear()
            self._ignore_rules.reset()

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        self.refresh()
        self._rebuild_executor.shutdown(wait=True)

    def __del__(self) -> None:
        if not self._shutdown:
            try:
                self.shutdown()
            except Exception:
                pass

    def _start_background_rebuild(self, root: Path) -> None:
        with self._rebuild_lock:  # one rebuild per root
            if root in self._active_rebuilds:
                return

            cancel_event = Event()
            done_event = Event()
            self._active_rebuilds[root] = _RebuildTask(
                cancel_event=cancel_event, done_event=done_event
            )

        try:
            self._rebuild_executor.submit(
                self._rebuild_worker, root, self._active_rebuilds[root]
            )
        except RuntimeError:
            with self._rebuild_lock:
                self._active_rebuilds.pop(root, None)
            done_event.set()

    def _rebuild_worker(self, root: Path, task: _RebuildTask) -> None:
        try:
            if task.cancel_event.is_set():  # cancelled before work began
                with self._rebuild_lock:
                    self._active_rebuilds.pop(root, None)
                return

            with self._rebuild_lock:  # bail if another root took ownership
                if self._target_root != root:
                    self._active_rebuilds.pop(root, None)
                    return

            with self._lock:  # exclusive access while rebuilding the store
                if task.cancel_event.is_set():
                    with self._rebuild_lock:
                        self._active_rebuilds.pop(root, None)
                    return

                self._store.rebuild(
                    root, should_cancel=lambda: task.cancel_event.is_set()
                )

            with self._rebuild_lock:
                self._active_rebuilds.pop(root, None)
        except Exception:
            with self._rebuild_lock:
                self._active_rebuilds.pop(root, None)
        finally:
            task.done_event.set()

    def _wait_for_rebuild(self, root: Path) -> None:
        with self._rebuild_lock:
            task = self._active_rebuilds.get(root)
        if task:
            task.done_event.wait()

    def _handle_watch_changes(
        self, root: Path, raw_changes: Iterable[tuple[Change, str]]
    ) -> None:
        normalized: list[tuple[Change, Path]] = []
        for change, path_str in raw_changes:
            if change not in {Change.added, Change.deleted, Change.modified}:
                continue
            normalized.append((change, Path(path_str).resolve()))

        if not normalized:
            return

        with self._lock:  # make watcher ignore stale roots
            if self._store.root != root:
                return
            self._store.apply_changes(normalized)
