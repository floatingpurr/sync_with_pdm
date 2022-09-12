from sync_with_pdm import __version__


def test_version() -> None:
    """Test version"""
    assert __version__ == "0.3.0"
