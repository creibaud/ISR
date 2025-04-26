import requests
from bs4 import BeautifulSoup

# URL cible
url = "https://www.generationpeche.fr/181-les-fiches-poissons.htm"

# Faire la requête HTTP
response = requests.get(url)

result = []

# Vérifier que la requête s'est bien passée
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    # Trouver la div avec l'id 'int-plante-tab'
    int_plante_tabs = soup.find_all("ul", class_="item")

    if int_plante_tabs:
        for tab in int_plante_tabs:
            # Récupérer tous les h3 à l'intérieur de chaque div
            h3_elements = tab.find_all("h2")

            # Afficher les textes
            for h3 in h3_elements:
                text = h3.get_text(strip=True)
                result.append(text.upper())
    else:
        print("Aucune div avec la classe 'int-plante-tab' trouvée sur la page.")
else:
    print(
        f"Erreur lors de la récupération de la page. Status code: {response.status_code}"
    )

print(result)
