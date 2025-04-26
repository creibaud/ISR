import json
from sentence_transformers import SentenceTransformer, util
import unidecode
import re


class FoodClassifierPro:
    def __init__(self, data_path):
        """
        Initialise le classificateur d'aliments amélioré

        Args:
            data_path (str): Chemin vers le fichier JSON contenant la hiérarchie des aliments
        """
        self.data_path = data_path
        self.data = self.load_data()
        self.categories, self.category_paths = self.extract_categories()

        # Charger le modèle d'embedding multilingue
        self.model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

        # Encoder toutes les catégories
        self.category_embeddings = self.model.encode(
            self.category_paths, convert_to_tensor=True
        )

    def load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize_text(self, text):
        text = text.lower()
        text = unidecode.unidecode(text)
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text

    def extract_categories(self):
        categories = []
        category_paths = []

        def recurse(items, path):
            for item in items:
                current_path = path + [item["name"]]
                categories.append(item["name"])
                category_paths.append(" > ".join(current_path))
                recurse(item.get("items", []), current_path)

        recurse(self.data, [])
        return categories, category_paths

    def suggest_category(self, ingredient_name, top_n=3):
        normalized_ingredient = self.normalize_text(ingredient_name)

        # Encoder l'ingrédient
        ingredient_embedding = self.model.encode(
            normalized_ingredient, convert_to_tensor=True
        )

        # Calcul de la similarité
        cosine_scores = util.cos_sim(ingredient_embedding, self.category_embeddings)[0]

        # Obtenir les meilleures correspondances
        top_results = cosine_scores.topk(k=top_n)

        suggestions = []
        for score, idx in zip(top_results.values, top_results.indices):
            suggestions.append(
                {"category_path": self.category_paths[idx], "score": float(score)}
            )

        return suggestions

    def add_new_ingredient(self, ingredient_name, category_path):
        """
        Ajoute un nouvel ingrédient à la catégorie spécifiée

        Args:
            ingredient_name (str): Nom de l'ingrédient
            category_path (str): Chemin de catégorie sous forme "Fruits > Agrumes"
        """
        path_parts = [part.strip() for part in category_path.split(">")]

        def find_category(items, path_index):
            if path_index >= len(path_parts):
                return None

            target_category = path_parts[path_index]
            for item in items:
                if item["name"] == target_category:
                    if path_index == len(path_parts) - 1:
                        return item
                    else:
                        return find_category(item.get("items", []), path_index + 1)

            return None

        category = find_category(self.data, 0)

        if category is not None:
            # Ajouter le nouvel ingrédient
            if "items" not in category:
                category["items"] = []
            category["items"].append(
                {"name": ingredient_name, "image": "", "items": []}
            )
            print(f"'{ingredient_name}' ajouté à '{category_path}'.")
        else:
            print("Catégorie introuvable. Aucun ingrédient ajouté.")

    def save_data(self, output_path="data_updated.json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"Données sauvegardées dans '{output_path}'.")


if __name__ == "__main__":
    # Exemple d'utilisation
    classifier = FoodClassifierPro("data.json")

    while True:
        print("\n===== CLASSIFICATION D'INGRÉDIENTS (PRO) =====")
        print("1. Classifier un nouvel ingrédient")
        print("2. Ajouter un ingrédient à une catégorie")
        print("3. Sauvegarder les modifications")
        print("4. Quitter")

        choice = input("\nVotre choix: ")

        if choice == "1":
            ingredient = input("\nNom de l'ingrédient: ")
            suggestions = classifier.suggest_category(ingredient)
            print(f"\nSuggestions pour '{ingredient}':")
            for i, suggestion in enumerate(suggestions):
                print(
                    f"{i+1}. {suggestion['category_path']} (score: {suggestion['score']:.2f})"
                )

        elif choice == "2":
            ingredient = input("\nNom de l'ingrédient à ajouter: ")
            category_path = input("\nChemin de la catégorie (ex: Fruits > Agrumes): ")
            classifier.add_new_ingredient(ingredient, category_path)

        elif choice == "3":
            output_file = (
                input("\nNom du fichier de sortie (par défaut: data_updated.json): ")
                or "data_updated.json"
            )
            classifier.save_data(output_file)

        elif choice == "4":
            print("\nAu revoir!")
            break

        else:
            print("\nChoix invalide. Veuillez réessayer.")
