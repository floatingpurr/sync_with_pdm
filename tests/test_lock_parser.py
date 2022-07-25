import tomlkit
from tomlkit.toml_file import TOMLFile

from sync_with_pdm.swp import PdmItems, PreCommitRepo


def test_pdm_items_creation() -> None:
    """Test PdmItems init"""
    lock = TOMLFile("pdm.lock")
    content = lock.read()
    assert isinstance(content["package"], tomlkit.items.AoT)
    p = PdmItems(content["package"], set())
    assert type(p._pdm_list) == list


def test_pdm_items_metadata() -> None:
    """Test PreCommitRepo metadata (returned by PdmItems.get_by_repo)"""
    lock = TOMLFile("pdm.lock")
    content = lock.read()
    assert isinstance(content["package"], tomlkit.items.AoT)
    p = PdmItems(content["package"], {"mypy"})
    item = p.get_by_repo("https://github.com/pre-commit/mirrors-mypy")
    assert type(item) == PreCommitRepo
    assert item.name == "mypy"
    assert item.repo == "https://github.com/pre-commit/mirrors-mypy"
    assert item.rev == "v0.971"
