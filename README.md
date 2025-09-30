# Aiai Manual – GitHub Sync

Detta repo innehåller en **automatisk export av Aiai-manualen** från Confluence till en statisk sajt (GitHub Pages).

## Så funkar det
- **Källan:** Confluence-spaces (definierade i `CONFLUENCE_SPACES` secret).  
- **Export:** Körs via GitHub Actions-workflow (`.github/workflows/sync.yml`).  
- **Innehåll:** Varje sida hämtas som HTML (`body.export_view`) och sparas i `docs/`.  
- **Portal:** `docs/index.html` visar:
  - Totalt antal sidor
  - Per-space sektioner med antal
  - **Sökruta per space** för att filtrera sidor
- **Tillgänglighet:** Publiceras på GitHub Pages och är öppet för web crawlers (AI-chatbot m.m.).

## Användning
- **Köra manuellt:**  
  Gå till **Actions → Sync Confluence Manual → Run workflow**.  
- **Schema:** Workflow kan köras automatiskt (t.ex. dagligen).

## Secrets
- `CONFLUENCE_USER` – en Confluence-användare (mailadress).  
- `CONFLUENCE_TOKEN` – API-token från Atlassian.  
- `CONFLUENCE_BASE` – t.ex. `https://kaustik.atlassian.net/wiki`.  
- `CONFLUENCE_SPACES` – kommaseparerade space-keys, MR,Ainstain  

## Vanliga justeringar
- **Lägga till fler spaces:** uppdatera `CONFLUENCE_SPACES`.  
- **Ändra portalens utseende:** editera `scripts/pull_confluence.py` (HTML-delen).  
- **Kolla antal sidor:** Se Actions-loggen efter körning.

---
