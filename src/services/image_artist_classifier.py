"""Image-based artist classification service using Hugging Face model hudaykulovf/mspcid."""

import io
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights
from huggingface_hub import hf_hub_download

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

REPO_ID = "hudaykulovf/mspcid"
MODEL_FILENAME = "results/models/resnet_finetune_model_v2.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Global singleton storage
_LOADED_MODEL = {}

ARTIST_INFO = {
    "Vincent van Gogh": {
        "movement": "Post-Impressionism",
        "period": "1853–1890 (Netherlands / France)",
        "signature_style": "Dramatic, impulsive brushwork, swirling lines, vibrant yellows and blues, high emotional intensity.",
        "iconic_works": "The Starry Night, Sunflowers, Cafe Terrace at Night, Bedroom in Arles",
    },
    "Claude Monet": {
        "movement": "Impressionism",
        "period": "1840–1926 (France)",
        "signature_style": "En plein air light diffusion, dappled brush strokes, reflections on water, atmospheric color palettes.",
        "iconic_works": "Water Lilies, Impression, Sunrise, Rouen Cathedral series, Haystacks",
    },
    "Pablo Picasso": {
        "movement": "Cubism / Modern Art",
        "period": "1881–1973 (Spain / France)",
        "signature_style": "Geometric deconstruction of forms, multi-perspective planes, bold outlines, Blue & Rose periods.",
        "iconic_works": "Guernica, Les Demoiselles d'Avignon, The Weeping Woman, Three Musicians",
    },
    "Salvador Dali": {
        "movement": "Surrealism",
        "period": "1904–1989 (Spain)",
        "signature_style": "Dreamlike illusions, melting clocks, hyper-realistic classical technique applied to surreal subconscious motifs.",
        "iconic_works": "The Persistence of Memory, Swans Reflecting Elephants, Metamorphosis of Narcissus",
    },
    "Henri Matisse": {
        "movement": "Fauvism / Modernism",
        "period": "1869–1954 (France)",
        "signature_style": "Explosive pure color harmonies, expressive flat planes, rhythmic contours, cut-out collages.",
        "iconic_works": "The Dance, Woman with a Hat, The Red Studio, Blue Nudes",
    },
    "Paul Cezanne": {
        "movement": "Post-Impressionism",
        "period": "1839–1906 (France)",
        "signature_style": "Structural brush strokes, geometric reduction of landscape, tonal planes bridging Impressionism to Cubism.",
        "iconic_works": "Mont Sainte-Victoire, The Card Players, The Bathers",
    },
    "Pierre-Auguste Renoir": {
        "movement": "Impressionism",
        "period": "1841–1919 (France)",
        "signature_style": "Luminous warmth, celebratory social gatherings, soft intimate portraits, shimmering light.",
        "iconic_works": "Luncheon of the Boating Party, Bal du moulin de la Galette, Dance at Le Moulin de la Galette",
    },
    "Amedeo Modigliani": {
        "movement": "Modernism / Expressionism",
        "period": "1884–1920 (Italy / France)",
        "signature_style": "Elongated necks and faces, almond-shaped stylized eyes, sculptural elegance influenced by African masks.",
        "iconic_works": "Portrait of Jeanne Hebuterne, Reclining Nude, Self-Portrait",
    },
    "Paul Gauguin": {
        "movement": "Post-Impressionism / Synthetism",
        "period": "1848–1903 (France / Tahiti)",
        "signature_style": "Bold flat color areas (cloisonnism), Tahitian mythology, exotic symbolism, earthy warmth.",
        "iconic_works": "Where Do We Come From? What Are We? Where Are We Going?, Tahitian Women on the Beach",
    },
    "Marc Chagall": {
        "movement": "Modern Surrealism / Folk Expressionism",
        "period": "1887–1985 (Belarus / France)",
        "signature_style": "Poetic floating figures, folklore motifs, stained-glass luminescence, dreamlike romance.",
        "iconic_works": "I and the Village, Over the Town, The Birthday",
    },
    "Camille Pissarro": {
        "movement": "Impressionism / Neo-Impressionism",
        "period": "1830–1903 (France)",
        "signature_style": "Rural landscapes, rustic village life, Parisian boulevards viewed from high angles, delicate pointillist touch.",
        "iconic_works": "Boulevard Montmartre, Spring, The Boulevard Montmartre at Night",
    },
    "Henri de Toulouse-Lautrec": {
        "movement": "Post-Impressionism / Art Nouveau",
        "period": "1864–1901 (France)",
        "signature_style": "Theatrical Parisian nightlife, Moulin Rouge cabaret dancers, dynamic linear caricatures and posters.",
        "iconic_works": "At the Moulin Rouge, Moulin Rouge: La Goulue, The Bed",
    },
    "Nicholas Roerich": {
        "movement": "Symbolism / Russian Modernism",
        "period": "1874–1947 (Russia / India)",
        "signature_style": "Monolithic Himalayan mountain peaks, spiritual mysticism, vivid azure and amber mineral pigments.",
        "iconic_works": "Song of Shambhala, Himalaya Series, Krishna: Spring in Kullu",
    },
    "Sam Francis": {
        "movement": "Abstract Expressionism / Tachisme",
        "period": "1923–1994 (USA)",
        "signature_style": "Lyrical paint splatters, expansive white space, luminous cellular dripping washes.",
        "iconic_works": "In Lovely Blueness, Shining Back, Around the Blues",
    },
    "William-Adolphe Bouguereau": {
        "movement": "Academic Art / Neoclassicism",
        "period": "1825–1905 (France)",
        "signature_style": "Photorealistic anatomical perfection, mythological narratives, smooth porcelain skin tones.",
        "iconic_works": "The Birth of Venus, Dante and Virgil, Song of the Angels",
    }
}


def _load_model_weights():
    """Downloads checkpoint from Hugging Face Space hudaykulovf/mspcid and initializes ResNet50."""
    if "model" in _LOADED_MODEL and "classes" in _LOADED_MODEL:
        return _LOADED_MODEL["model"], _LOADED_MODEL["classes"], _LOADED_MODEL["preprocess"], _LOADED_MODEL["last_conv"]

    model_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type="space",
        filename=MODEL_FILENAME,
    )

    ckpt = torch.load(model_path, map_location=DEVICE)
    class_names = ckpt["classes"]

    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    last_conv = model.layer4
    preprocess = weights.transforms()

    _LOADED_MODEL["model"] = model
    _LOADED_MODEL["classes"] = class_names
    _LOADED_MODEL["preprocess"] = preprocess
    _LOADED_MODEL["last_conv"] = last_conv

    return model, class_names, preprocess, last_conv


if HAS_STREAMLIT:
    load_cached_image_model = st.cache_resource(show_spinner=False)(_load_model_weights)
else:
    load_cached_image_model = _load_model_weights


def make_gradcam_heatmap(input_tensor, model, target_layer, pred_index=None):
    """Computes Grad-CAM attention heatmap for the target layer."""
    activations = {}
    gradients = {}

    def forward_hook(module, inp, out):
        out.requires_grad_(True)
        activations["value"] = out

    def backward_hook(module, grad_in, grad_out):
        gradients["value"] = grad_out[0]

    h1 = target_layer.register_forward_hook(forward_hook)
    h2 = target_layer.register_full_backward_hook(backward_hook)

    model.zero_grad()
    scores = model(input_tensor)
    if pred_index is None:
        pred_index = scores.argmax(dim=1).item()

    target_score = scores[:, pred_index]
    target_score.backward(retain_graph=True)

    h1.remove()
    h2.remove()

    A = activations["value"][0]
    G = gradients["value"][0]

    weights = G.mean(dim=(1, 2))
    cam = torch.relu((weights[:, None, None] * A).sum(dim=0))
    cam = cam.detach().cpu().numpy()
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    return cam


def overlay_heatmap(original_pil: Image.Image, heatmap: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Blends colormapped heatmap over the original image."""
    import matplotlib as mpl

    orig_size = original_pil.size
    heatmap_resized = Image.fromarray(np.uint8(255 * heatmap)).resize(orig_size, Image.BILINEAR)
    heat_norm = np.array(heatmap_resized) / 255.0

    cmap = mpl.colormaps["jet"]
    colored = cmap(heat_norm)[:, :, :3]
    colored_pil = Image.fromarray((colored * 255).astype("uint8"))

    blended = Image.blend(original_pil.convert("RGB"), colored_pil, alpha=alpha)
    return blended


class ImageArtistClassifierService:
    """Service wrapping Hugging Face space hudaykulovf/mspcid for image-based artist detection."""

    def __init__(self):
        self.repo_id = REPO_ID

    def predict(self, image_input: Any, top_k: int = 5) -> Dict[str, Any]:
        """Runs image-based artist classification and Grad-CAM generation."""
        model, class_names, preprocess, last_conv = load_cached_image_model()

        if isinstance(image_input, (bytes, bytearray)):
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif hasattr(image_input, "read"):
            pil_img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        else:
            raise ValueError("Unsupported image input type.")

        x = preprocess(pil_img).unsqueeze(0).to(DEVICE)
        x.requires_grad_(True)

        heatmap = make_gradcam_heatmap(x, model, last_conv)
        blended_cam = overlay_heatmap(pil_img, heatmap)

        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)[0].detach().cpu().numpy()

        sorted_indices = probs.argsort()[::-1]
        all_preds = []
        for idx in sorted_indices:
            name = class_names[idx]
            p = float(probs[idx])
            all_preds.append({
                "artist": name,
                "probability": p,
                "percentage": round(p * 100, 2),
            })

        top_match = all_preds[0]
        artist_meta = ARTIST_INFO.get(top_match["artist"], {
            "movement": "Fine Art Master",
            "period": "Classical to Modern Era",
            "signature_style": "Characteristic brush strokes and palette recognized by the fine-tuned vision model.",
            "iconic_works": "Acclaimed studio collection.",
        })

        return {
            "top_artist": top_match["artist"],
            "top_confidence": top_match["percentage"],
            "predictions": all_preds[:top_k],
            "all_predictions": all_preds,
            "gradcam_image": blended_cam,
            "original_image": pil_img,
            "artist_meta": artist_meta,
            "model_source": "Hugging Face · hudaykulovf/mspcid (ResNet-50)",
        }
