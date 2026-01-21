import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sys
from pathlib import Path

INPUT_CSV = "tous_les_articles.csv"
OUTPUT_CSV = "articles_complets.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

DELAI_MIN = 2
DELAI_MAX = 4

def scrape_article(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # TITRE
        h1 = soup.find("h1")
        titre = h1.get_text(strip=True) if h1 else ""

        # DATE
        date = ""
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get("datetime", "").strip()

        # CONTENU
        content = ""
        for selector in [
            "div.article-content",
            "div.content",
            "article",
            "main"
        ]:
            bloc = soup.select_one(selector)
            if bloc:
                content = bloc.decode_contents()
                break

        return {
            "titre": titre,
            "date": date,
            "contenu": content
        }

    except Exception as e:
        print(f"Erreur sur {url} : {e}")
        return None


def main():
    if not Path(INPUT_CSV).exists():
        print("CSV d'entrée introuvable")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)

    # Colonnes si absentes
    for col in ["Titre_final", "Date", "Contenu"]:
        if col not in df.columns:
            df[col] = ""

    total = len(df)
    print(f"{total} articles à traiter\n")

    for i, row in df.iterrows():
        if pd.notna(row["Contenu"]) and row["Contenu"].strip():
            continue  # déjà fait

        url = row["URL"]
        print(f"{i+1}/{total} → {url}")

        data = scrape_article(url)
        if data:
            df.at[i, "Titre_final"] = data["titre"]
            df.at[i, "Date"] = data["date"]
            df.at[i, "Contenu"] = data["contenu"]
            print("   OK")
        else:
            print("   Échec")

        # sauvegarde progressive
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

        pause = random.uniform(DELAI_MIN, DELAI_MAX)
        print(f"Pause {pause:.1f}s\n")
        time.sleep(pause)

    print("Terminé ! Données complètes sauvegardées.")


if __name__ == "__main__":
    main()
