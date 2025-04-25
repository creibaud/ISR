import requests
from bs4 import BeautifulSoup
import json


def extract_data_from_html(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        list_posts_div = soup.find("div", class_="list-posts-vertus")

        data = []

        if list_posts_div:
            images = list_posts_div.find_all(
                "img", class_="thumbnail-blog wp-post-image"
            )

            links = list_posts_div.find_all("a", class_="post-title")

            for img, link in zip(images, links):
                img_src = img.get("src")

                link_text = link.get_text().strip()

                data.append({"title": link_text, "image_url": img_src})

            return data
        else:
            print("La div 'list-posts-vertus' n'a pas été trouvée sur la page.")
    else:
        print(
            f"Erreur lors de la récupération de la page, statut : {response.status_code}"
        )


def get_index_of_item(item, data):
    for index, d in enumerate(data):
        if d["title"] == item:
            return index
    return -1


url = "https://www.france-mineraux.fr/nutrition/aliments/"
data = extract_data_from_html(url)

url2 = "https://www.france-mineraux.fr/aliments-nutriments/"
uris = [
    "cereales-et-farines",
    "epices-herbes-aromatiques-et-condiments",
    "fromages-cremes-et-produits-laitiers",
    "fruits-et-fruits-exotiques",
    "fruits-secs-et-fruits-a-coques",
    "legumes-et-legumineuses",
    "poissons-crustaces-et-fruits-de-mer",
    "viandes-rouges-et-blanches",
]

for uri in uris:
    new_data = extract_data_from_html(url2 + uri)
    for item in new_data:
        i = get_index_of_item(item["title"], data)
        if i != -1:
            data[i]["category"] = uri

with open("data.json", "w") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
    print("Data saved to data.json")
