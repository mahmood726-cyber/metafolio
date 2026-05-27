"""Build a standalone MetaFolio HTML artifact from merged portfolio JSON."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_paths(project_root=None, merged_input=None, template_path=None, output_path=None):
    root = Path(project_root).resolve() if project_root else PROJECT_ROOT
    return {
        "input": Path(merged_input).resolve() if merged_input else root / "data" / "portfolios_merged.json",
        "template": Path(template_path).resolve() if template_path else root / "template.html",
        "output": Path(output_path).resolve() if output_path else root / "metafolio.html",
    }


def render_html(merged_json: str, template_html: str) -> str:
    if "</script>" in merged_json.lower():
        raise ValueError("Unsafe JSON payload contains </script>")
    if "__DATA_PLACEHOLDER__" not in template_html:
        raise ValueError("Template is missing __DATA_PLACEHOLDER__")
    return template_html.replace("__DATA_PLACEHOLDER__", merged_json)


def main(project_root=None, merged_input=None, template_path=None, output_path=None):
    paths = resolve_paths(
        project_root=project_root,
        merged_input=merged_input,
        template_path=template_path,
        output_path=output_path,
    )
    merged_json = paths["input"].read_text(encoding="utf-8")
    template_html = paths["template"].read_text(encoding="utf-8")
    html = render_html(merged_json, template_html)
    paths["output"].write_text(html, encoding="utf-8")
    print(f"JSON size: {len(merged_json)} chars")
    print(f"Written: {paths['output']}")
    return paths["output"]


if __name__ == "__main__":
    main()
