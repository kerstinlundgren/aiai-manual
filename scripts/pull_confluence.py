import os, requests, pathlib, html, time

BASE    = os.environ["CONFLUENCE_BASE"].rstrip("/")
SPACES  = [s.strip() for s in os.environ["CONFLUENCE_SPACES"].split(",")]
USER    = os.environ["CONFLUENCE_USER"]
TOKEN   = os.environ["CONFLUENCE_TOKEN"]

out = pathlib.Path("docs")
out.mkdir(exist_ok=True)

def fetch_all_pages(space):
    start, limit = 0, 200   # 200 är max Confluence tillåter
    pages = []
    while True:
        r = sess.get(
            f"{BASE}/rest/api/content",
            params={
                "spaceKey": space,
                "limit": limit,
                "start": start,
                "expand": "body.export_view",
                "type": "page"
            },
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            break
        pages.extend(results)
        # använd 'start' från API-svaret om det finns
        if not data.get("_links", {}).get("next"):
            break
        start += limit
        time.sleep(0.2)
    return pages

index = ['<!doctype html><meta charset="utf-8"><title>Aiai manual</title><h1>Manual</h1><ul>']

for space in SPACES:
    pages = fetch_all_pages(space)
    index.append(f"<h2>Space: {html.escape(space)}</h2><ul>")
    for p in pages:
        title = p.get("title", "Untitled")
        pid   = p.get("id")
        body  = p.get("body", {}).get("export_view", {}).get("value", "")
        fname = f"{space}-{pid}.html"
        with open(out/fname, "w", encoding="utf-8") as f:
            f.write(
                f"<!doctype html><meta charset='utf-8'>"
                f"<title>{html.escape(title)}</title>"
                f"<h1>{html.escape(title)}</h1>{body}"
            )
        index.append(f"<li><a href='{fname}'>{html.escape(title)}</a></li>")
    index.append("</ul>")

index.append("</ul>")
with open(out/"index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(index))

with open(out/"robots.txt", "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")

print("Fetched spaces:", ", ".join(SPACES))
