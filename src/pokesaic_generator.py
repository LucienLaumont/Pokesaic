import numpy as np
from PIL import Image
from skimage.color import rgb2lab
from src.KDTree_generator import PokemonColorKDTree
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # ✅ barre de progression


class PokemonMosaicCreator:
    """Crée des mosaïques avec des cartes Pokémon basées sur les couleurs LAB"""
    
    def __init__(self, kdtree_path='data\\kdtree\\pokemon_kdtree.pkl', tile_size=(177, 250)):
        """
        Initialise le créateur de mosaïque
        """
        print(f"⚡ Chargement du KDTree depuis {kdtree_path}...")

        # ✅ On réutilise la méthode existante
        color_tree = PokemonColorKDTree.load_kdtree(kdtree_path)

        self.kdtree = color_tree.kdtree
        self.cards = color_tree.cards
        self.lab_colors = color_tree.lab_colors
        self.tile_size = tile_size
        self.card_cache = {}

        print(f"✅ Prêt ! {len(self.cards)} cartes indexées")
    
    def compute_mosaic_grid(self, image_path, card_size=(177, 250), scale=1):
        """
        Calcule la grille (cols, rows) et adapte l'image à une mosaïque Pokémon.
        Plus le scale est grand, plus il y a de cartes (mosaïque plus fine).
        """
        img = Image.open(image_path).convert('RGB')
        w, h = img.size
        card_w, card_h = card_size

        cols = max(1, int((w / card_w) * scale))
        rows = max(1, int((h / card_h) * scale))

        mosaic_w = cols * card_w
        mosaic_h = rows * card_h
        resized_img = img.resize((mosaic_w, mosaic_h), Image.Resampling.LANCZOS)

        return resized_img, cols, rows

    def rgb_to_lab(self, rgb):
        """Convertit RGB en LAB"""
        rgb_normalized = rgb.astype(np.float32) / 255.0
        lab = rgb2lab(rgb_normalized)
        return lab
    
    def load_card_image(self, card):
        """Charge une image de carte avec cache"""
        image_path = card['image_path']
        
        if image_path in self.card_cache:
            return self.card_cache[image_path]
        
        try:
            img = Image.open(image_path).convert('RGB')
            img_resized = img.resize(self.tile_size, Image.Resampling.LANCZOS)
            self.card_cache[image_path] = img_resized
            return img_resized
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {image_path}: {e}")
            return Image.new('RGB', self.tile_size, (0, 0, 0))

    def create_mosaic(self, image_path, scale=1, output_path="data\\output\\mosaic_output.png", workers=8):
        """
        Crée la mosaïque Pokémon à partir d'une image donnée.
        """
        # 1️⃣ Adapter l'image à la grille
        resized_img, cols, rows = self.compute_mosaic_grid(image_path, self.tile_size, scale)
        print(f"🧮 Image adaptée à une grille de {cols} colonnes x {rows} lignes")

        # 2️⃣ Découper l'image en tuiles
        tile_w, tile_h = self.tile_size
        tiles = []
        for y in tqdm(range(rows), desc="🧩 Découpage des tuiles", unit="ligne"):
            for x in range(cols):
                left, top = x * tile_w, y * tile_h
                tile = resized_img.crop((left, top, left + tile_w, top + tile_h))
                tiles.append(tile)

        # 3️⃣ Calcul des couleurs dominantes LAB (vectorisé + parallélisé)
        def compute_lab(tile):
            np_tile = np.array(tile, dtype=np.float32) / 255.0
            lab_tile = rgb2lab(np_tile)
            return lab_tile.reshape(-1, 3).mean(axis=0)

        print("🎨 Calcul des couleurs dominantes (Lab)...")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            tile_lab_colors = list(tqdm(
                executor.map(compute_lab, tiles),
                total=len(tiles),
                desc="   → Conversion LAB",
                unit="tuile"
            ))
        tile_lab_colors = np.array(tile_lab_colors, dtype=np.float32)

        # 4️⃣ Recherche des cartes les plus proches via KDTree
        print("🔍 Recherche des cartes les plus proches dans le KDTree...")
        _, indices = self.kdtree.query(tile_lab_colors, k=1)
        matched_cards = [self.cards[i] for i in indices]
        
        # 5️⃣ Assemblage final
        print("🧱 Assemblage de la mosaïque finale...")
        mosaic = Image.new('RGB', (cols * tile_w, rows * tile_h))
        for idx, card in enumerate(tqdm(matched_cards, desc="   → Placement des cartes", unit="carte")):
            card_img = self.load_card_image(card)
            x = (idx % cols) * tile_w
            y = (idx // cols) * tile_h
            mosaic.paste(card_img, (x, y))

        # 6️⃣ Sauvegarde
        mosaic.save(output_path)
        print(f"✅ Mosaïque sauvegardée dans {output_path}")
        return mosaic
