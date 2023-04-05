import logging
import os
import shutil
from pathlib import Path
from typing import List

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

logger = logging.getLogger(__name__)


def get_gitignore_rules(gitignore_path: Path) -> List[str]:
    rules = []
    if gitignore_path.exists():
        with gitignore_path.open("r") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(line)
    return rules


def get_unignored_files(
    root_path: Path,
    folder_path: Path,
    parent_rules: List[str] = [],
    ignore_spec: str = ".copyignore",
) -> List[str]:
    if folder_path is None:
        folder_path = root_path

    if root_path is None:
        root_path = folder_path

    unignored_files = []

    gitignore_path = folder_path / ignore_spec
    if gitignore_path.exists():
        local_rules = get_gitignore_rules(gitignore_path)
    else:
        local_rules = []

    all_rules = parent_rules + local_rules
    path_spec = PathSpec.from_lines(GitWildMatchPattern, all_rules)

    for entry in folder_path.iterdir():
        relative_path = str(entry.relative_to(root_path))

        if entry.is_file() and not path_spec.match_file(relative_path) and not entry.name == ignore_spec:
            unignored_files.append(relative_path)
        elif entry.is_dir() and not path_spec.match_file(relative_path):
            unignored_files.extend(
                get_unignored_files(
                    root_path=root_path,
                    folder_path=entry,
                    parent_rules=all_rules,
                    ignore_spec=ignore_spec,
                )
            )
        else:
            logger.debug("Ignoring %s", relative_path)

    return unignored_files


def copy_files(source_path: Path, target_path: Path, unignored_files: List[str]) -> None:
    num_to_be_copied = len(unignored_files)
    file_size = 0

    for file_path in unignored_files:
        source_file = source_path / file_path
        target_file = target_path / file_path
        if not target_file.parent.exists():
            target_file.parent.mkdir(parents=True)
        file_size += os.path.getsize(source_file)
        logger.debug("Copying %s to %s", source_file, target_file)
        shutil.copy(source_file, target_file)
    return num_to_be_copied, file_size / 1024 / 1024
