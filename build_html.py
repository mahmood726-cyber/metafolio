import json

with open('C:/MetaFolio/data/portfolios_merged.json', 'r') as f:
    merged_json = f.read()

# Safety check
assert '</script>' not in merged_json.lower(), "DANGER: </script> in JSON!"
print(f"JSON size: {len(merged_json)} chars")

html = open('C:/MetaFolio/template.html', 'r', encoding='utf-8').read()
html = html.replace('__DATA_PLACEHOLDER__', merged_json)

with open('C:/MetaFolio/metafolio.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Written: {len(html)} chars, {html.count(chr(10))} lines")
