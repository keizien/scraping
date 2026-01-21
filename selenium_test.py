import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

BASE_URL = "https://compta.webwin.be"
MAX_PAGES = 230

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

all_articles = {}
session = requests.Session()
session.headers.update(HEADERS)

print("Démarrage récupération de TOUS les articles")

for page in range(1, MAX_PAGES + 1):
    url = f"{BASE_URL}/search?numPage={page}"
    print(f"\n Page {page}")

    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("a.item[href]")

        if not links:
            print("Aucun lien trouvé → on continue")
            continue

        nouveaux = 0

        for a in links:
            href = a["href"].strip()
            titre = a.get_text(strip=True)

            if not href.startswith("http"):
                href = BASE_URL + href

            if href not in all_articles:
                all_articles[href] = titre
                nouveaux += 1

        print(f"{nouveaux} nouveaux articles")
        print(f"Total cumulé : {len(all_articles)}")

        pause = random.uniform(6, 12)
        print(f"Pause {pause:.1f}s")
        time.sleep(pause)

    except Exception as e:
        print(f"Erreur page {page} : {e}")
        time.sleep(15)

df = pd.DataFrame(
    [{"Titre": t, "URL": u} for u, t in all_articles.items()]
)
df.to_csv("tous_les_articles.csv", index=False, encoding="utf-8-sig")

print(f"\n TERMINÉ : {len(df)} articles sauvegardés")
