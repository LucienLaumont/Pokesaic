import json
import pickle
import numpy as np
from scipy.spatial import KDTree
from pathlib import Path

class PokemonColorKDTree:
    """
    Classe pour créer et gérer un KDTree des couleurs LAB des cartes Pokémon
    """
    
    def __init__(self, json_path=None, kdtree=None, cards=None, lab_colors=None):
        """
        Initialise le KDTree à partir d'un fichier JSON
        """
        self.json_path = json_path
        self.series = []
        self.cards = cards or []
        self.lab_colors = lab_colors
        self.kdtree = kdtree
        
    def load_data(self):
        """Charge les données depuis le JSON"""
        print(f"📂 Chargement des données depuis {self.json_path}...")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.series = json.load(f)
        
        # Aplatir toutes les cartes de toutes les séries
        self.cards = [
            {**card, "series_name": series["series_name"], "series_code": series["series_code"]}
            for series in self.series
            for card in series["cards"]
            if "lab_color" in card
        ]
        
        # Extraire les couleurs LAB
        self.lab_colors = np.array([card["lab_color"] for card in self.cards], dtype=np.float32)
        
        print(f"{len(self.cards)} cartes chargées")
        print(f"Dimensions LAB: {self.lab_colors.shape}")
        
    def build_kdtree(self, leafsize=10):
        """Construit le KDTree"""
        print(f"Construction du KDTree (leafsize={leafsize})...")
        self.kdtree = KDTree(self.lab_colors, leafsize=leafsize)
        print("KDTree construit avec succès")
    
    def save_kdtree(self, output_path='data\\pokemon_kdtree.pkl'):
        """Sauvegarde le KDTree et les métadonnées"""
        print(f"Sauvegarde du KDTree dans {output_path}...")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data_to_save = {
            'kdtree': self.kdtree,
            'cards': self.cards,
            'lab_colors': self.lab_colors
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(data_to_save, f)
        
        print("KDTree sauvegardé avec succès")
        
    @classmethod
    def load_kdtree(cls, path):
        """Charge un KDTree et les données associées"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        return cls(
            kdtree=data['kdtree'],
            cards=data['cards'],
            lab_colors=data['lab_colors']
        )
