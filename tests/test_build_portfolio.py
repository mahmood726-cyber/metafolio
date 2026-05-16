import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_portfolio import main, resolve_paths


def test_main_uses_repo_relative_sibling_projects(tmp_path):
    projects_root = tmp_path / 'projects'
    project_root = projects_root / 'MetaFolio'
    project_root.mkdir(parents=True)

    paths = resolve_paths(project_root=project_root, projects_root=projects_root)
    paths['input'].parent.mkdir(parents=True, exist_ok=True)
    paths['input'].write_text(
        json.dumps([{
            'review_id': 'CD000001',
            'analysis_name': 'Synthetic portfolio',
            'k': 3,
            'yi': [0.1, 0.15, 0.2],
            'sei': [0.1, 0.12, 0.11],
        }]),
        encoding='utf-8',
    )

    out_path = main(project_root=project_root, projects_root=projects_root)

    payload = json.loads(out_path.read_text(encoding='utf-8'))
    assert out_path == project_root / 'data' / 'portfolios.json'
    assert len(payload) == 1
    assert payload[0]['review_id'] == 'CD000001'
    assert payload[0]['enumeration_method'] == 'exhaustive'
    assert payload[0]['n_subsets_evaluated'] == 7
