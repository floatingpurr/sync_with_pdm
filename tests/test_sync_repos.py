import pathlib
from unittest.mock import patch

import pytest
from py._path.local import LocalPath

from sync_with_pdm import swp
from tests.helpers import CONFIG_CONTENT, get_repo_version

LEN_CONFIG_CONTENT = CONFIG_CONTENT.count("\n")
PATH = pathlib.Path(__file__).parent.resolve()


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # sync only dev dependencies
        (
            {"all": False, "skip": []},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.971",     # bumped (dev)
                "https://github.com/pycqa/flake8": "3.9.0",                 # not bumped (optional)
                "https://github.com/psf/black": "21.5b2",                   # not bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by pdm
            },
            # fmt: on
        ),
        # sync all dependencies (all = True)
        (
            {"all": True, "skip": []},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.971",     # bumped (dev)
                "https://github.com/pycqa/flake8": "4.0.1",                 # bumped (optional)
                "https://github.com/psf/black": "22.6.0",                   # bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by pdm
            },
            # fmt: on
        ),
        # sync all dependencies (all = True), skipping mypy
        (
            {"all": True, "skip": ["mypy"]},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.812",     # not bumped (dev), skipped
                "https://github.com/pycqa/flake8": "4.0.1",                 # bumped (dev)
                "https://github.com/psf/black": "22.6.0",                   # bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by pdm
            },
            # fmt: on
        ),
        # sync dev dependencies, skipping `black` and  `flake8`
        (
            {"all": False, "skip": ["black", "flake8"]},
            # fmt: off
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.971",     # bumped (dev)
                "https://github.com/pycqa/flake8": "3.9.0",                 # not bumped (dev)
                "https://github.com/psf/black": "21.5b2",                   # not bumped (main)
                "https://github.com/pycqa/isort": "5.10.1",                 # not managed by pdm
            },
            # fmt: on
        ),
    ],
)
@patch("sync_with_pdm.swp.PYPROJECT_FILE", PATH / "pyproject_test.toml")
def test_sync_repos(tmpdir: LocalPath, test_input: dict, expected: dict) -> None:
    """Test repo synchronization against different inputs and configurations"""

    config_file = tmpdir.join(".pre-commit-yaml")
    config_file.write(CONFIG_CONTENT)

    retv = swp.sync_repos(PATH / "pdm_test.lock", **test_input, config=config_file.strpath)  # type: ignore

    for repo in expected:
        assert get_repo_version(config_file.strpath, repo) == expected[repo]

    assert LEN_CONFIG_CONTENT == len(open(config_file.strpath).readlines())
    assert retv == 1


@patch("sync_with_pdm.swp.PYPROJECT_FILE", PATH / "pyproject_test.toml")
def test_no_change(tmpdir: LocalPath) -> None:
    """Test a run without updates"""
    config_file = tmpdir.join(".pre-commit-yaml")
    config_file.write(CONFIG_CONTENT)
    retv = swp.sync_repos(
        PATH / "pdm_test.lock",  # type: ignore
        all=False,
        skip=["mypy", "flake8"],
        config=config_file.strpath,
    )
    assert retv == 0
