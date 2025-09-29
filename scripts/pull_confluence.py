import os, requests, pathlib, html, time

# Miljövariabler från GitHub Secrets
BASE   = os.environ["CONFLUENCE_BASE"].rstrip("/")
SPACE  = os.environ["CONFLUENCE_SPACE"]
USER   = os.environ["CONFLUENCE_USER"]
TOKEN  = os.environ["CONFLUENCE_TOKEN"]

out = pathlib.Path("docs")
out.mkdir(exist_ok=True)

# Hämta alla sidor i spacet, paginerat
def fetch_all_pages():
    start, limit = 0, 100
    pages = []
    sess = requests.Session()
    sess.auth = (USER, TOKEN)
    while True:
        r = sess.get(
            f"{BASE}/rest/api/content",
            params={
                "spaceKey": SPACE,
                "type": "page",
                "start": start,
                "limit": limit,
                "expand": "body.export_view"
            },
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            break
        pages.extend(results)
        if len(results) < limit:
            break
        start += limit
        time.sleep(0.2)  # snällt mot API:t
    return pages

pages = fetch_all_pages()

# Bygg index + en HTML-fil per sida
index = [
    '<!doctype html><meta charset="utf-8"><title>Aiai manual</title>',
    '<h1>Aiai manual</h1><ul>'
]

for p in pages:
    title = p.get("title", "Untitled")
    pid   = p.get("id")
    body  = p.get("body", {}).get("export_view", {}).get("value", "")
    fname = f"{pid}.html"
    with open(out/fname, "w", encoding="utf-8") as f:
        f.write(
            f"<!doctype html><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title>"
            f"<h1>{html.escape(title)}</h1>{body}"
        )
    index.append(f"<li><a href='{fname}'>{html.escape(title)}</a></li>")

index.append("</ul>")
with open(out/"index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(index))

# Tillåt crawlers
with open(out/"robots.txt", "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")

print(f"Klar: skrev {len(pages)} sidor till docs/")
