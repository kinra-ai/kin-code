from __future__ import annotations

from collections.abc import Callable
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from kin_code.core.paths.config_paths import resolve_local_skills_dir
from kin_code.core.paths.global_paths import GLOBAL_SKILLS_DIR
from kin_code.core.skills.models import SkillInfo, SkillMetadata
from kin_code.core.skills.parser import SkillParseError, parse_frontmatter
from kin_code.core.utils import name_matches

if TYPE_CHECKING:
    from kin_code.core.config import VibeConfig

logger = getLogger("kin_code")


class SkillManager:
    """Manages skill discovery and retrieval.

    Skills are markdown-based instruction sets that enhance agent capabilities.
    Each skill is a directory containing a SKILL.md file with YAML frontmatter
    defining metadata and the skill's instructions in the body.

    Skills are discovered from:

    1. User-configured skill_paths from VibeConfig
    2. Local .kin/skills/ directory in the current working directory
    3. Global skills directory (~/.config/kin/skills/)

    The manager uses a first-wins strategy: if multiple skills have the same
    name, the first one discovered (based on search path order) is used.

    Attributes:
        available_skills: Dictionary mapping skill names to SkillInfo objects,
            filtered by enabled_skills/disabled_skills config.

    Example:
        Basic usage::

            from kin_code.core.config import VibeConfig
            from kin_code.core.skills.manager import SkillManager

            config = VibeConfig.load()
            manager = SkillManager(config_getter=lambda: config)

            # List all available skills
            for name, info in manager.available_skills.items():
                print(f"{name}: {info.description}")
                print(f"  Tags: {', '.join(info.tags)}")

        Retrieving skill content::

            # Get a specific skill
            if (skill := manager.get_skill("docs-writer")) is not None:
                # Access skill metadata
                print(f"Name: {skill.name}")
                print(f"Description: {skill.description}")
                print(f"Path: {skill.skill_path}")

                # Read the full skill content for injection
                content = skill.skill_path.read_text()
                print(f"Instructions: {content}")

        Skill file structure::

            # Skills are organized as:
            # ~/.config/kin/skills/
            #   my-skill/
            #     SKILL.md          # Required: frontmatter + instructions
            #     supporting.py     # Optional: additional files

            # SKILL.md format:
            # ---
            # name: my-skill
            # description: Does something useful
            # tags: [coding, refactoring]
            # ---
            # Instructions for the agent go here...

        Filtering skills::

            # Skills respect enabled_skills/disabled_skills in config
            # In config.toml:
            # enabled_skills = ["docs-*", "re:^test-.*"]
            # disabled_skills = ["experimental-*"]

            # Only matching skills appear in available_skills
            filtered = manager.available_skills
    """

    def __init__(self, config_getter: Callable[[], VibeConfig]) -> None:
        self._config_getter = config_getter
        self._search_paths = self._compute_search_paths(self._config)
        self._available: dict[str, SkillInfo] = self._discover_skills()

        if self._available:
            logger.info(
                "Discovered %d skill(s) from %d search path(s)",
                len(self._available),
                len(self._search_paths),
            )

    @property
    def _config(self) -> VibeConfig:
        return self._config_getter()

    @property
    def available_skills(self) -> dict[str, SkillInfo]:
        if self._config.enabled_skills:
            return {
                name: info
                for name, info in self._available.items()
                if name_matches(name, self._config.enabled_skills)
            }
        if self._config.disabled_skills:
            return {
                name: info
                for name, info in self._available.items()
                if not name_matches(name, self._config.disabled_skills)
            }
        return dict(self._available)

    @staticmethod
    def _compute_search_paths(config: VibeConfig) -> list[Path]:
        paths: list[Path] = []

        for path in config.skill_paths:
            if path.is_dir():
                paths.append(path)

        if (skills_dir := resolve_local_skills_dir(Path.cwd())) is not None:
            paths.append(skills_dir)

        if GLOBAL_SKILLS_DIR.path.is_dir():
            paths.append(GLOBAL_SKILLS_DIR.path)

        unique: list[Path] = []
        for p in paths:
            rp = p.resolve()
            if rp not in unique:
                unique.append(rp)

        return unique

    def _discover_skills(self) -> dict[str, SkillInfo]:
        """Discover all skills from configured search paths.

        Scans each search path for subdirectories containing a SKILL.md file.
        Skills are indexed by name, with earlier paths taking precedence when
        duplicate names are found (first-wins strategy).

        Returns:
            Dictionary mapping skill names to their SkillInfo objects.
        """
        skills: dict[str, SkillInfo] = {}
        for base in self._search_paths:
            if not base.is_dir():
                continue
            for name, info in self._discover_skills_in_dir(base).items():
                if name not in skills:
                    skills[name] = info
                else:
                    logger.debug(
                        "Skipping duplicate skill '%s' at %s (already loaded from %s)",
                        name,
                        info.skill_path,
                        skills[name].skill_path,
                    )
        return skills

    def _discover_skills_in_dir(self, base: Path) -> dict[str, SkillInfo]:
        skills: dict[str, SkillInfo] = {}
        for skill_dir in base.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            if (skill_info := self._try_load_skill(skill_file)) is not None:
                skills[skill_info.name] = skill_info
        return skills

    def _try_load_skill(self, skill_file: Path) -> SkillInfo | None:
        try:
            skill_info = self._parse_skill_file(skill_file)
        except Exception as e:
            logger.warning("Failed to parse skill at %s: %s", skill_file, e)
            return None
        return skill_info

    def _parse_skill_file(self, skill_path: Path) -> SkillInfo:
        try:
            content = skill_path.read_text(encoding="utf-8")
        except OSError as e:
            raise SkillParseError(f"Cannot read file: {e}") from e

        frontmatter, _ = parse_frontmatter(content)
        metadata = SkillMetadata.model_validate(frontmatter)

        skill_name_from_dir = skill_path.parent.name
        if metadata.name != skill_name_from_dir:
            logger.warning(
                "Skill name '%s' doesn't match directory name '%s' at %s",
                metadata.name,
                skill_name_from_dir,
                skill_path,
            )

        return SkillInfo.from_metadata(metadata, skill_path)

    def get_skill(self, name: str) -> SkillInfo | None:
        return self.available_skills.get(name)
