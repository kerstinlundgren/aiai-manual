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

def ensure_expand(url: str) -> str:
    # Se till att expand-parametern alltid följer med i pagineringen
    if "expand=" not in url:
        url += ("&" if "?" in url else "?") + "expand=content.body.export_view"
    return url

def fetch_all_pages(space: str):
    """Hämtar alla 'page' i ett space och ser till att expand följer med via _links.next."""
    results = []
    url = f"{BASE}/rest/api/search"
    params = {
        "cql": f'space="{space}" AND type=page',
        "limit": 200,
        "expand": "content.body.export_view"
    }
    while True:
        r = sess.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        nxt = data.get("_links", {}).get("next")
        if not nxt:
            break
        url = ensure_expand(BASE + nxt)
        params = None  # redan inbakat i next-länken
        time.sleep(0.2)
    return results

def fetch_body_by_id(page_id: str) -> str:
    """Fallback: hämta sidans HTML-kropp direkt per ID om export_view saknas i sökresultatet."""
    r = sess.get(f"{BASE}/rest/api/content/{page_id}",
                 params={"expand": "body.export_view"})
    r.raise_for_status()
    data = r.json()
    return (data.get("body", {}) \
                .get("export_view", {}) \
                .get("value", "")) or ""

def write_page(space: str, content: dict):
    """Skriver en Confluence-sida som HTML-fil. Hämtar fallback-kropp om den saknas."""
    c = content.get("content", {})
    title = c.get("title", "Untitled")
    pid   = c.get("id")
    body  = (c.get("body") or {}).get("export_view", {}).get("value", "")

    if not body and pid:
        # Fallback: hämta sidkropp per ID om den inte följde med i search-svaret
        try:
            body = fetch_body_by_id(pid)
        except Exception as e:
            print(f"[warn] No body for page {pid} ({title}): {e}")
            body = ""

    fname = f"{space}-{pid}.html"
    with open(out / fname, "w", encoding="utf-8") as f:
        f.write(
            f"<!doctype html><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title>"
            f"<h1>{html.escape(title)}</h1>{body}"
        )
    return fname, title

# ----- Index-HTML med totalsiffra och sök per space -----

index_lines = [
    '<!doctype html><html><head><meta charset="utf-8"><title>Aiai manual</title>',
    '<style>body{font-family:Arial,sans-serif;max-width:800px;margin:auto;} input{margin:0.5em 0;padding:0.5em;width:100%;} li{margin:0.2em 0;}</style>',
    '<script>',
    'function filterList(spaceId){',
    '  let q=document.getElementById("search-"+spaceId).value.toLowerCase();',
    '  let items=document.querySelectorAll("#list-"+spaceId+" li");',
    '  items.forEach(li=>{ li.style.display = li.textContent.toLowerCase().includes(q) ? "" : "none"; });',
    '}',
    '</script></head><body>',
    '<h1>Aiai manual</h1>',
]

total_written = 0
space_counts = {}

for idx, space in enumerate(SPACES):
    pages = fetch_all_pages(space)
    space_id = f"{idx}"
    count = 0

    index_lines.append(f"<h2>Space: {html.escape(space)} ({len(pages)} pages)</h2>")
    index_lines.append(f'<input type="text" id="search-{space_id}" onkeyup="filterList(\'{space_id}\')" placeholder="Search in {html.escape(space)}...">')
    index_lines.append(f"<ul id='list-{space_id}'>")

    for p in pages:
        fname, title = write_page(space, p)
        index_lines.append(f"<li><a href='{fname}'>{html.escape(title)}</a></li>")
        total_written += 1
        count += 1

    index_lines.append("</ul>")
    space_counts[space] = count

# Totalsiffra överst
index_lines.insert(10, f"<p><b>Total pages across all spaces: {total_written}</b></p>")

index_lines.append("</body></html>")

with open(out/"index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))

with open(out/"robots.txt", "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")

for space, count in space_counts.items():
    print(f"Space {space}: {count} pages")
print(f"Total: {total_written} pages written to docs/")
