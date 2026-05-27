import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_html import main, render_html


def test_main_uses_repo_relative_defaults(tmp_path):
    project_root = tmp_path / "MetaFolio"
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "portfolios_merged.json").write_text('{"ok": true}', encoding="utf-8")
    (project_root / "template.html").write_text(
        "<html><body><script>const DATA = __DATA_PLACEHOLDER__;</script></body></html>",
        encoding="utf-8",
    )

    out_path = main(project_root=project_root)

    assert out_path == project_root / "metafolio.html"
    rendered = out_path.read_text(encoding="utf-8")
    assert '{"ok": true}' in rendered
    assert "__DATA_PLACEHOLDER__" not in rendered


def test_render_html_rejects_script_termination():
    with pytest.raises(ValueError, match="</script>"):
        render_html('{"bad":"</script>"}', "<script>__DATA_PLACEHOLDER__</script>")


def test_render_html_requires_placeholder():
    with pytest.raises(ValueError, match="__DATA_PLACEHOLDER__"):
        render_html('{"ok":true}', "<html></html>")
