#!/usr/bin/env python3
"""
Compute the Transcendent Invariant Kernel embedding Φ.

1. Collect 999 statements (333 per tradition)
2. Embed via all-mpnet-base-v2
3. PCA to remove culture-specific axes
4. Compute centroid = Φ
"""

import json
import numpy as np
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Tradition source texts (excerpts for seeding — expand to 333 per tradition)
# ---------------------------------------------------------------------------

CHRIST_TEACHINGS_SEEDS = [
    "Blessed are the poor in spirit, for theirs is the kingdom of heaven.",
    "Blessed are those who mourn, for they shall be comforted.",
    "Blessed are the meek, for they shall inherit the earth.",
    "Blessed are the merciful, for they shall receive mercy.",
    "Blessed are the peacemakers, for they shall be called children of God.",
    "Love your enemies and pray for those who persecute you.",
    "Do not judge, so that you may not be judged.",
    "In everything do to others as you would have them do to you.",
    "What does it profit a man to gain the whole world and forfeit his soul?",
    "Let anyone among you who is without sin be the first to throw a stone.",
    "Whatever you did for one of the least of these, you did for me.",
    "The truth will set you free.",
    "Forgive, and you will be forgiven.",
    "It is more blessed to give than to receive.",
    "Do not be overcome by evil, but overcome evil with good.",
]

KANTIAN_SEEDS = [
    "Act only according to that maxim whereby you can at the same time will that it should become a universal law.",
    "Treat humanity, whether in your own person or in the person of any other, always as an end and never merely as a means.",
    "Every rational being exists as an end in himself, not merely as a means to be arbitrarily used.",
    "Two things fill the mind with ever new and increasing admiration: the starry heavens above me and the moral law within me.",
    "Morality is not the doctrine of how we may make ourselves happy, but of how we may make ourselves worthy of happiness.",
    "Freedom is the alone unoriginated birthright of man.",
    "Dignity has no price and admits of no equivalent.",
    "A good will is good not because of what it effects or accomplishes.",
    "Autonomy of the will is the supreme principle of morality.",
    "Act so that the maxim of your action could be willed as universal law of nature.",
    "The categorical imperative is the principle of duty.",
    "Persons are not things and therefore are not to be used merely as means.",
    "Rational beings are called persons because their nature already marks them out as ends in themselves.",
    "Nothing in the world can be called good without qualification except a good will.",
    "Duty is the necessity of acting from respect for the moral law.",
]

UBUNTU_SEEDS = [
    "A person is a person through other persons — umuntu ngumuntu ngabantu.",
    "I am because we are, and since we are, therefore I am.",
    "If you want to go fast, go alone. If you want to go far, go together.",
    "A person with ubuntu is welcoming, hospitable, warm, generous, willing to share.",
    "Ubuntu speaks to the very essence of being human — we are interconnected.",
    "Your pain is my pain. My wealth is your wealth. Your salvation is my salvation.",
    "Ubuntu means that people are people through other people.",
    "It is not I think therefore I am, but rather I participate therefore I am.",
    "A traveler through a country would stop at a village and not have to ask for food or water.",
    "The quality of ubuntu gives people resilience, enabling them to survive and emerge as humans.",
    "Ubuntu is the belief in a universal bond of sharing that connects all humanity.",
    "One cannot be human in isolation — our humanity is bound up in one another.",
    "Ubuntu is about compassion, community, and concern for the well-being of others.",
    "A person with ubuntu knows that he or she is diminished when others are humiliated.",
    "The root of ubuntu is: I am human because I belong, I participate, I share.",
]


def expand_statements(seeds: List[str], target_n: int = 333,
                       tradition_name: str = "") -> List[str]:
    """
    Expand seed statements to target_n via:
    1. Using seeds as-is
    2. Generating variations (paraphrases, related principles)
    
    In practice, this should use an LLM to generate 333 diverse statements
    from each tradition's source texts. For now, we repeat + augment.
    """
    statements = list(seeds)
    
    # Simple augmentation: prefix variations
    prefixes = [
        "The principle states that ",
        "It is taught that ",
        "One must remember that ",
        "The tradition holds that ",
        "A core teaching is: ",
    ]
    
    i = 0
    while len(statements) < target_n:
        base = seeds[i % len(seeds)]
        prefix = prefixes[i % len(prefixes)]
        statements.append(f"{prefix}{base.lower()}")
        i += 1
    
    return statements[:target_n]


def compute_kernel(output_path: str = "data/processed/kernel_phi.npz",
                   n_per_tradition: int = 333,
                   pca_remove: int = 3,
                   reg_lambda: float = 0.01):
    """
    Compute Φ = centroid of tradition embeddings after PCA debiasing.
    """
    from sentence_transformers import SentenceTransformer
    from sklearn.decomposition import PCA
    
    print("Loading sentence-transformers model...")
    model = SentenceTransformer("all-mpnet-base-v2")
    
    # Expand statements
    print("Preparing tradition statements...")
    christ = expand_statements(CHRIST_TEACHINGS_SEEDS, n_per_tradition, "Christ")
    kantian = expand_statements(KANTIAN_SEEDS, n_per_tradition, "Kantian")
    ubuntu = expand_statements(UBUNTU_SEEDS, n_per_tradition, "Ubuntu")
    
    all_statements = christ + kantian + ubuntu
    labels = (["christ"] * n_per_tradition + 
              ["kantian"] * n_per_tradition + 
              ["ubuntu"] * n_per_tradition)
    
    # Embed
    print(f"Embedding {len(all_statements)} statements...")
    embeddings = model.encode(all_statements, show_progress_bar=True, 
                               normalize_embeddings=True)
    embeddings = np.array(embeddings)
    
    # PCA to remove culture-specific axes
    print(f"Removing top-{pca_remove} culture-specific PCA components...")
    pca = PCA(n_components=pca_remove)
    culture_components = pca.fit_transform(embeddings)
    
    # Project out culture-specific directions
    projection_matrix = pca.components_.T @ pca.components_
    debiased = embeddings - embeddings @ projection_matrix
    
    # Compute centroid with regularization
    print("Computing kernel centroid Φ...")
    phi = np.mean(debiased, axis=0)
    
    # Regularize: L2 penalty
    phi = phi / (np.linalg.norm(phi) + reg_lambda)
    
    # Also compute per-tradition centroids (for Table 4)
    tradition_centroids = {}
    for trad in ["christ", "kantian", "ubuntu"]:
        mask = np.array([l == trad for l in labels])
        trad_emb = debiased[mask]
        centroid = np.mean(trad_emb, axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + reg_lambda)
        tradition_centroids[trad] = centroid
    
    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path,
             phi=phi,
             christ_centroid=tradition_centroids["christ"],
             kantian_centroid=tradition_centroids["kantian"],
             ubuntu_centroid=tradition_centroids["ubuntu"],
             pca_components=pca.components_,
             pca_explained_variance=pca.explained_variance_ratio_)
    
    print(f"Kernel saved to {output_path}")
    print(f"  Φ shape: {phi.shape}")
    print(f"  Φ norm: {np.linalg.norm(phi):.4f}")
    print(f"  PCA explained variance: {pca.explained_variance_ratio_}")
    
    # Cross-tradition similarity
    for t1, c1 in tradition_centroids.items():
        for t2, c2 in tradition_centroids.items():
            if t1 < t2:
                sim = np.dot(c1, c2)
                print(f"  cos({t1}, {t2}) = {sim:.4f}")
    
    return phi, tradition_centroids


def compute_alignment(question_text: str, phi: np.ndarray,
                       model=None) -> float:
    """Compute alignment score: cos(embed(q), Φ)."""
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-mpnet-base-v2")
    
    q_emb = model.encode([question_text], normalize_embeddings=True)[0]
    return float(np.dot(q_emb, phi))


if __name__ == "__main__":
    compute_kernel()
