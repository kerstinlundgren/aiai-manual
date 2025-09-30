import os, requests, pathlib, html, time

BASE    = os.environ["CONFLUENCE_BASE"].rstrip("/")
USER    = os.environ["CONFLUENCE_USER"]
TOKEN   = os.environ["CONFLUENCE_TOKEN"]
SPACES  = [s.strip() for s in os.environ["CONFLUENCE_SPACES"].split(",")]

out = pathlib.Path("docs")
out.mkdir(exist_ok=True)

sess = requests.Session()
sess.auth = (USER, TOKEN)
sess.headers.update({"Accept": "application/json"})


def fetch_all_pages(space):
    """Hämtar alla sidor i ett space med paginering via _links.next"""
    results = []
    url = f"{BASE}/rest/api/search?cql=space=\"{space}\" AND type=page&limit=200"
    while url:
        r = sess.get(url)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        next_link = data.get("_links", {}).get("next")
        if next_link:
            url = BASE + next_link
            time.sleep(0.2)  # snällt mot API:t
        else:
            url = None
    return results


def write_page(space, content):
    """Sparar en Confluence-sida som HTML"""
    c = content["content"]
    title = c.get("title", "Untitled")
    pid   = c.get("id")
    body  = (c.get("body") or {}).get("export_view", {}).get("value", "")
    fname = f"{space}-{pid}.html"
    with open(out/fname, "w", encoding="utf-8") as f:
        f.write(
            f"<!doctype html><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title>"
            f"<h1>{html.escape(title)}</h1>{body}"
        )
    return fname, title


index_lines = [
    '<!doctype html><meta charset="utf-8"><title>Aiai manual</title>',
    '<h1>Aiai manual</h1>'
]

total_written = 0
space_counts = {}

for space in SPACES:
    index_lines.append(f"<h2>Space: {html.escape(space)}</h2><ul>")
    pages = fetch_all_pages(space)
    count = 0
    for p in pages:
        fname, title = write_page(space, p)
        index_lines.append(f"<li><a href='{fname}'>{html.escape(title)}</a></li>")
        total_written += 1
        count += 1
    index_lines.append("</ul>")
    space_counts[space] = count

# Skriv index.html
with open(out/"index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))

# robots.txt för att tillåta crawlers
with open(out/"robots.txt", "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")

# Logga summering
for space, count in space_counts.items():
    print(f"Space {space}: {count} pages")
print(f"Total: {total_written} pages written to docs/")
