import requests
from bs4 import BeautifulSoup
import csv

# URL de la page
url = "https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/"

# Faire la requête
response = requests.get(url)

result = []

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    # Récupérer tous les <td>
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            if cols:
                result.append(cols)

        # Écrire les résultats dans un fichier CSV
        with open("fromages.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Nom", "Description"])  # En-têtes du fichier CSV
            writer.writerows(result)
else:
    print(
        f"Erreur lors de la récupération de la page. Status code: {response.status_code}"
    )

print(result)
