"""Song artist classification service using Hugging Face tjl223/song-artist-classifier-v2."""

import os
from typing import Any, Dict, List, Optional
import torch

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

MODEL_ID = "tjl223/song-artist-classifier-v2"

# Ensure clean huggingface warnings on windows
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Global singleton storage for non-streamlit contexts
_LOADED_COMPONENTS = {}


def _load_model_and_tokenizer():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if "model" in _LOADED_COMPONENTS and "tokenizer" in _LOADED_COMPONENTS:
        return _LOADED_COMPONENTS["model"], _LOADED_COMPONENTS["tokenizer"]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    model.eval()

    _LOADED_COMPONENTS["tokenizer"] = tokenizer
    _LOADED_COMPONENTS["model"] = model
    return model, tokenizer


if HAS_STREAMLIT:
    load_cached_classifier = st.cache_resource(show_spinner=False)(_load_model_and_tokenizer)
else:
    load_cached_classifier = _load_model_and_tokenizer


PRESET_LYRICS: Dict[str, Dict[str, str]] = {
    "Taylor Swift — Shake It Off": {
        "artist": "Taylor Swift",
        "text": "Cause the players gonna play, play, play, play, play\nAnd the haters gonna hate, hate, hate, hate, hate\nBaby, I'm just gonna shake, shake, shake, shake, shake\nI shake it off, I shake it off\nHeartbreakers gonna break, break, break, break, break\nAnd the fakers gonna fake, fake, fake, fake, fake",
    },
    "Taylor Swift — Blank Space": {
        "artist": "Taylor Swift",
        "text": "Got a long list of ex-lovers\nThey'll tell you I'm insane\n'Cause you know I love the players\nAnd you love the game\n'Cause we're young and we're reckless\nWe'll take this way too far\nIt'll leave you breathless or with a nasty scar",
    },
    "Drake — God's Plan": {
        "artist": "Drake",
        "text": "I've been movin' calm, don't start no trouble with me\nTryna keep it peaceful is a struggle for me\nDon't pull up at 6 AM to cuddle with me\nYou know how I like it when you lovin' on me\nI don't wanna die for them to miss me\nYes, I see the things that they wishin' on me",
    },
    "Drake — Hotline Bling": {
        "artist": "Drake",
        "text": "You used to call me on my cell phone\nLate night when you need my love\nCall me on my cell phone\nLate night when you need my love\nAnd I know when that hotline bling\nThat can only mean one thing",
    },
    "The Weeknd — Blinding Lights": {
        "artist": "The Weeknd",
        "text": "I've been on my own for long enough\nMaybe you can show me how to love, maybe\nI'm going through withdrawals\nYou don't even have to do too much\nYou can turn me on with just a touch, baby\nI look around and Sin City's cold and empty",
    },
    "The Weeknd — Starboy": {
        "artist": "The Weeknd",
        "text": "I'm tryna put you in the worst mood, ah\nP1 cleaner than your church shoes, ah\nMilli point two just to hurt you, ah\nAll red Lamb' just to tease you, ah\nNone of these toys on lease too, ah\nLook what you've done, I'm a starboy",
    },
    "Olivia Rodrigo — Drivers License": {
        "artist": "Olivia Rodrigo",
        "text": "I got my driver's license last week\nJust like we always talked about\n'Cause you were so excited for me\nTo finally drive up to your house\nBut today I drove through the suburbs\nCrying 'cause you weren't around",
    },
    "Olivia Rodrigo — Good 4 U": {
        "artist": "Olivia Rodrigo",
        "text": "Well, good for you, I guess you moved on really easily\nYou found a new girl and it only took a couple weeks\nRemember when you said that you wanted to give me the world?\nAnd good for you, I guess that you've been workin' on yourself\nI guess that therapist I found for you, she really helped",
    },
    "SZA — Kill Bill": {
        "artist": "SZA",
        "text": "I might kill my ex, not the best idea\nHis new girlfriend's next, how'd I get here?\nI might kill my ex, I still love him though\nRather be in jail than alone\nI did it all for love, did it all on no drugs",
    },
    "Doja Cat — Paint The Town Red": {
        "artist": "Doja Cat",
        "text": "Yeah, bitch, I said what I said\nI'd rather be famous instead\nI let all that get to my head\nI don't care, I paint the town red\nBitch, I'm attractive, I can get passive\nWalk up in the room, whole party go silent",
    },
    "Nicki Minaj — Super Bass": {
        "artist": "Nicki Minaj",
        "text": "Boy, you got my heartbeat runnin' away\nBeating like a drum and it's coming your way\nCan't you hear that boom, badoom, boom, boom, badoom, boom, bass?\nHe got that super bass\nThis one is for the boys with the boomin' system\nTop down, AC with the cooler system",
    },
    "Travis Scott — Sicko Mode": {
        "artist": "Travis Scott",
        "text": "Sun is down, freezin' cold\nThat's how we already know winter's here\nMy dawg would pull up on you with that stick\nWent to sleep and got the yard lit\nOut like a light, like a light\nSlept through the flight",
    },
    "21 Savage — Bank Account": {
        "artist": "21 Savage",
        "text": "I buy a new car for the bitch\nI got 1-2-3-4-5-6-7-8 M's in my bank account, yeah\nIn my bank account, yeah\nIn my bank account, yeah\nFast car, Nascar, racecar",
    },
    "Dua Lipa — Levitating": {
        "artist": "Dua Lipa",
        "text": "If you wanna run away with me, I know a galaxy\nAnd I can take you for a ride\nI had a premonition that we fell into a rhythm\nWhere the music don't stop for life\nGlitter in the sky, glitter in my eyes\nShining just the way I like",
    },
    "Jack Harlow — First Class": {
        "artist": "Jack Harlow",
        "text": "I been living lifestyle, I been living flight now\nI could put you in first class, up in the sky\nI could put you in first class, get you high\nSweet honey iced tea, I know what you like\nPineapple juice, don't need no ice",
    },
    "Morgan Wallen — Last Night": {
        "artist": "Morgan Wallen",
        "text": "Last night we let the liquor talk\nI can't remember everything we said but we said it all\nYou told me that you wish I was somebody you never met\nBut baby, baby something's telling me this ain't over yet\nNo way it was our last night",
    },
    "Zach Bryan — Something in the Orange": {
        "artist": "Zach Bryan",
        "text": "It'll be fine by the dusk light I'm tellin' you, baby\nThese things eat at your bones and drive your young mind crazy\nIt tells me that you're never comin' back\nTo you I'm just a man, to me you're all I am\nWhere the hell did I go wrong?",
    },
    "Luke Combs — Fast Car": {
        "artist": "Luke Combs",
        "text": "You got a fast car\nI want a ticket to anywhere\nMaybe we make a deal\nMaybe together we can get somewhere\nAny place is better\nStarting from zero, got nothing to lose",
    },
    "Megan Thee Stallion — Savage": {
        "artist": "Megan Thee Stallion",
        "text": "I'm a savage, yeah\nClassy, bougie, ratchet, yeah\nSassy, moody, nasty, yeah\nActing stupid, what's happening?\nBitch, what's happening?\nBitch, I'm a boss, I'm a leader",
    },
    "Noah Kahan — Stick Season": {
        "artist": "Noah Kahan",
        "text": "And I love Vermont, but it's the season of the sticks\nAnd I saw your mom, she forgot that I existed\nAnd it's half my fault, but I just start to freak out\nNow I'm stuck here, all alone\nForgive my northern attitude, I was raised on little light",
    },
    "Chris Stapleton — Tennessee Whiskey": {
        "artist": "Chris Stapleton",
        "text": "You're as smooth as Tennessee whiskey\nYou're as sweet as strawberry wine\nYou're as warm as a glass of brandy\nAnd honey, I stay stoned on your love all the time\nI've looked for love in all the same old places",
    },
    "Jelly Roll — Need a Favor": {
        "artist": "Jelly Roll",
        "text": "I only talk to God when I need a favor\nAnd I only pray when I ain't got a prayer\nSo who the hell am I, who the hell am I\nTo expect a savior oh, when I only talk to God if I need a favor?",
    },
    "The Grateful Dead — Ripple": {
        "artist": "The Grateful Dead",
        "text": "If my words did glow with the gold of sunshine\nAnd my tunes were played on the harp unstrung\nWould you hear my voice come through the music\nWould you hold it near as it were your own?\nRipple in still water, when there is no pebble tossed",
    },
}


class ArtistClassifierService:
    """Service wrapping Hugging Face DistilBERT tjl223/song-artist-classifier-v2."""

    def __init__(self):
        self.model_id = MODEL_ID

    def is_model_available(self) -> bool:
        try:
            load_cached_classifier()
            return True
        except Exception:
            return False

    def predict_artist(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        """Classifies song lyrics or snippet into predicted artist probabilities."""
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            raise ValueError("Please provide song lyrics or a textual excerpt to classify.")

        model, tokenizer = load_cached_classifier()

        inputs = tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1).detach().cpu()

        # Map to label names from model config
        id2label = model.config.id2label
        all_results = []
        for idx, prob_tensor in enumerate(probs):
            prob = float(prob_tensor.item())
            all_results.append({
                "artist": id2label.get(idx, f"Artist {idx}"),
                "probability": prob,
                "percentage": round(prob * 100, 2),
            })

        all_results.sort(key=lambda x: x["probability"], reverse=True)

        top_match = all_results[0]
        return {
            "model_id": self.model_id,
            "top_artist": top_match["artist"],
            "top_confidence": top_match["percentage"],
            "predictions": all_results[:top_k],
            "all_predictions": all_results,
        }
