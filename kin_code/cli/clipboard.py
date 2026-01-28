from __future__ import annotations

import base64
from collections.abc import Callable
import os
import platform
import shutil
import subprocess

import pyperclip
from textual.app import App

_PREVIEW_MAX_LENGTH = 40


def _copy_osc52(text: str) -> None:
    """Copy text to clipboard using OSC 52 escape sequence.

    Works in terminals that support OSC 52, including through SSH and tmux.
    Writes directly to /dev/tty to bypass any output buffering.

    Args:
        text: Text to copy to clipboard.
    """
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    osc52_seq = f"\033]52;c;{encoded}\a"
    if os.environ.get("TMUX"):
        osc52_seq = f"\033Ptmux;\033{osc52_seq}\033\\"

    with open("/dev/tty", "w") as tty:
        tty.write(osc52_seq)
        tty.flush()


def _copy_x11_clipboard(text: str) -> None:
    """Copy text to clipboard using xclip on X11 systems.

    Args:
        text: Text to copy to clipboard.

    Raises:
        subprocess.CalledProcessError: If xclip command fails.
    """
    subprocess.run(
        ["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True
    )


def _copy_wayland_clipboard(text: str) -> None:
    """Copy text to clipboard using wl-copy on Wayland systems.

    Args:
        text: Text to copy to clipboard.

    Raises:
        subprocess.CalledProcessError: If wl-copy command fails.
    """
    subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)


def _has_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _get_copy_fns(app: App) -> list[Callable[[str], None]]:
    """Build prioritized list of clipboard copy functions for the current platform.

    Returns platform-appropriate copy methods, with native Linux tools (xclip,
    wl-copy) taking priority when available, followed by OSC 52, pyperclip,
    and the Textual app's built-in clipboard method.

    Args:
        app: Textual application instance for fallback clipboard access.

    Returns:
        List of copy functions to try in order of preference.
    """
    copy_fns: list[Callable[[str], None]] = [
        _copy_osc52,
        pyperclip.copy,
        app.copy_to_clipboard,
    ]
    if platform.system() == "Linux" and _has_cmd("wl-copy"):
        copy_fns = [_copy_wayland_clipboard, *copy_fns]
    if platform.system() == "Linux" and _has_cmd("xclip"):
        copy_fns = [_copy_x11_clipboard, *copy_fns]
    return copy_fns


def _shorten_preview(texts: list[str]) -> str:
    """Create a truncated preview string for clipboard notification.

    Joins multiple text selections with return symbols and truncates
    to fit within the preview length limit.

    Args:
        texts: List of selected text fragments.

    Returns:
        Condensed preview string with newlines shown as return symbols.
    """
    dense_text = "⏎".join(texts).replace("\n", "⏎")
    if len(dense_text) > _PREVIEW_MAX_LENGTH:
        return f"{dense_text[: _PREVIEW_MAX_LENGTH - 1]}…"
    return dense_text


def copy_selection_to_clipboard(app: App) -> None:
    """Copy all selected text from the application to the system clipboard.

    Gathers text selections from all widgets in the app, combines them,
    and attempts to copy using multiple clipboard methods. Shows a
    notification indicating success or failure.

    Args:
        app: Textual application instance to search for selections.
    """
    selected_texts = []

    for widget in app.query("*"):
        if not hasattr(widget, "text_selection") or not widget.text_selection:
            continue

        selection = widget.text_selection

        try:
            result = widget.get_selection(selection)
        except Exception:
            continue

        if not result:
            continue

        selected_text, _ = result
        if selected_text.strip():
            selected_texts.append(selected_text)

    if not selected_texts:
        return

    combined_text = "\n".join(selected_texts)

    success = False
    copy_fns = _get_copy_fns(app)

    for copy_fn in copy_fns:
        try:
            copy_fn(combined_text)
        except:
            pass
        else:
            success = True

    if success:
        app.notify(
            f'"{_shorten_preview(selected_texts)}" copied to clipboard',
            severity="information",
            timeout=2,
            markup=False,
        )
    else:
        app.notify(
            "Failed to copy - no clipboard method available",
            severity="warning",
            timeout=3,
        )
