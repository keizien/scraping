import pandas as pd
import requests
import time
from pathlib import Path

SITE_URL = "https://www.compta-fiscal.be"
API_ENDPOINT = f"{SITE_URL}/wp-json/wp/v2/posts"
OUTPUT_CSV = "articles_compta_fiscal_complets.csv"

def get_all_posts():
    posts = []
    page = 1
    total_pages = None
    
    while True:
        print(f"Page {page}{f'/{total_pages}' if total_pages else ''}...", end=" ")
        
        params = {
            "per_page": 100,
            "page": page
        }
        
        try:
            r = requests.get(API_ENDPOINT, params=params, timeout=30)
            
            if not total_pages and 'X-WP-TotalPages' in r.headers:
                total_pages = int(r.headers['X-WP-TotalPages'])
                total_posts = r.headers.get('X-WP-Total', '?')
                print(f"\n Total: {total_posts} articles sur {total_pages} pages\n")
            
            if r.status_code == 400:  
                print("Fin")
                break
            
            r.raise_for_status()
            data = r.json()
            
            if not data:
                print("Fin")
                break
            
            for post in data:
                posts.append({
                    "titre": post.get("title", {}).get("rendered", "").strip(),
                    "url": post.get("link", ""),
                    "date": post.get("date", ""),
                    "contenu_html": post.get("content", {}).get("rendered", ""),
                    "extrait": post.get("excerpt", {}).get("rendered", "").strip()
                })
            
            print(f"{len(data)} articles (total: {len(posts)})")
            page += 1
            time.sleep(0.3)  
            
        except requests.exceptions.Timeout:
            print(f"Timeout - Réessai dans 5s...")
            time.sleep(5)
            continue
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau: {e}")
            break
            
        except Exception as e:
            print(f"Erreur: {e}")
            break
    
    return posts

print("Scraping de compta-fiscal.be via API WordPress")
print(f"Endpoint: {API_ENDPOINT}\n")
print("="*60 + "\n")

start_time = time.time()
all_posts = get_all_posts()

if all_posts:
    df = pd.DataFrame(all_posts)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print(f"SUCCÈS !")
    print(f"{len(all_posts)} articles sauvegardés")
    print(f"Fichier: {OUTPUT_CSV}")
    print(f"Temps: {elapsed/60:.1f} minutes")
    print(f"Chemin complet: {Path(OUTPUT_CSV).absolute()}")
    
    print("\nAperçu des 3 premiers articles:")
    print(df[['titre', 'date']].head(3).to_string(index=False))
    
else:
    print("\n Aucun article récupéré")
    print("Vérifie que l'API est bien accessible:")
    print(f"→ {API_ENDPOINT}?per_page=5")