import requests

url = "https://www.data.gouv.fr/fr/datasets/r/17f7cfd9-a5fe-4b6a-9f5d-3625feaa396e"
print(f"📥 Téléchargement depuis {url}")

response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Taille: {len(response.content)} bytes")

with open('radars_downloaded.csv', 'wb') as f:
    f.write(response.content)

print("✅ Fichier téléchargé avec succès")

# Test rapide
import csv
with open('radars_downloaded.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    count = sum(1 for _ in reader)
    print(f"📊 {count} lignes dans le fichier téléchargé")
