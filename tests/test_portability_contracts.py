import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "e156-submission" / "config.json"
PORTABLE_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "build_html.py",
    REPO_ROOT / "build_portfolio.py",
    CONFIG_PATH,
]


def test_submission_config_uses_repo_relative_root():
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert payload["path"] == ".."
    assert (CONFIG_PATH.parent / payload["path"]).resolve() == REPO_ROOT.resolve()


def test_release_surface_has_no_hardcoded_metafolio_root():
    for path in PORTABLE_FILES:
        text = path.read_text(encoding="utf-8")
        assert r"C:\MetaFolio" not in text, path
        assert "C:/MetaFolio" not in text, path
