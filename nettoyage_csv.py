import pandas as pd
import html
from bs4 import BeautifulSoup

df = pd.read_csv("articles_compta_fiscal_complets.csv")

def nettoyer_titre(titre_brut):
    titre = html.unescape(str(titre_brut))
    
    soup = BeautifulSoup(titre, 'html.parser')
    titre = soup.get_text()

    if len(titre) > 100:
        titre = titre[:100].rsplit(' ', 1)[0] + '...'
    
    return titre.strip()

df['titre'] = df['titre'].apply(nettoyer_titre)

df.to_csv("articles_compta_fiscal.csv", index=False, encoding="utf-8-sig")

print("Titres nettoyés !")
print("\n Aperçu:")
for i in range(5):
    print(f"{i+1}. {df['titre'].iloc[i]}")
