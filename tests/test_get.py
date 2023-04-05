import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from clean_copy.clean_copy import get_gitignore_rules, get_unignored_files

IGNORE_SPEC = ".copyignore"


def create_test_files(temp_dir: Path, files_and_dirs: List[str]) -> None:
    for path in files_and_dirs:
        new_path = temp_dir / path
        if not new_path.parent.exists():
            new_path.parent.mkdir(parents=True)
        if path.endswith("/"):
            new_path.mkdir(parents=True)
        else:
            new_path.touch()


def test_get_gitignore_rules() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        gitignore_content = ["*.log", "# This is a comment", "temp/"]
        gitignore_file = temp_dir / IGNORE_SPEC
        with gitignore_file.open("w") as f:
            f.write("\n".join(gitignore_content))

        rules = get_gitignore_rules(gitignore_file)
        assert rules == ["*.log", "temp/"]


def test_get_unignored_files() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        create_test_files(
            temp_dir,
            [
                "file1.txt",
                "file2.log",
                "dir1/",
                "dir1/file3.txt",
                "dir1/file4.log",
                "dir2/",
                "dir2/.copyignore",
                "dir2/file5.txt",
                "dir2/file6.log",
            ],
        )

        gitignore_content = ["*.log"]
        gitignore_file = temp_dir / IGNORE_SPEC
        with gitignore_file.open("w") as f:
            f.write("\n".join(gitignore_content))

        gitignore_content = ["*.txt"]
        gitignore_file = temp_dir / "dir2" / IGNORE_SPEC
        with gitignore_file.open("w") as f:
            f.write("\n".join(gitignore_content))

        expected_files = [
            "file1.txt",
            "dir1/file3.txt",
        ]

        unignored_files = get_unignored_files(temp_dir, None, [], IGNORE_SPEC)
        assert sorted(unignored_files) == sorted(expected_files)
