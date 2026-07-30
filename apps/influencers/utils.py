import re
import spacy
from langdetect import detect_langs, LangDetectException

# Singleton-like loading of spaCy model to avoid repeated disk I/O
_NLP_MODEL = None

def get_nlp_model():
    global _NLP_MODEL
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    return _NLP_MODEL

def clean_text_for_nlp(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'\S+@\S+', '', text)                # Remove emails
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text) # Remove phone numbers
    
    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF" u"\U0001F1E0-\U0001F1FF"
    "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    text = re.sub(r'[@#](\w+)', r'\1', text)           # Keep hashtag/mention text, remove symbol
    text = re.sub(r'[^a-z0-9\s]', ' ', text)           # Remove punctuation/special chars
    text = re.sub(r'\s+', ' ', text).strip()           # Remove extra spaces
    return text

def detect_language(text: str) -> dict:
    if not text or len(text) < 10:
        return {"code": "unknown", "name": "Unknown", "confidence": 0.0}
    try:
        langs = detect_langs(text)
        top_lang = langs[0]
        code = top_lang.lang
        confidence = top_lang.prob
        name = "Hindi" if code == 'hi' else "English" if code == 'en' else code.title()
        return {"code": code, "name": name, "confidence": round(confidence, 2)}
    except LangDetectException:
        return {"code": "unknown", "name": "Unknown", "confidence": 0.0}

def extract_nlp_features(text: str) -> dict:
    nlp = get_nlp_model()
    doc = nlp(text)
    
    keywords = set()
    # Extract lemmatized noun chunks
    for chunk in doc.noun_chunks:
        lemma = chunk.root.lemma_.lower().strip()
        if lemma and not chunk.root.is_stop and len(lemma) > 2:
            keywords.add(lemma)
            
    # Extract individual important nouns/proper nouns
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.lemma_) > 2:
            keywords.add(token.lemma_.lower())
            
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
            
    return {"keywords": list(keywords), "entities": entities}

# Configurable keyword groups for rule-based scoring
KEYWORD_GROUPS = {
    "government_schemes": ["digital india", "startup india", "skill india", "pm kisan", "upi", "make in india", "swachh bharat", "ayushman bharat", "viksit bharat", "modi", "narendra modi"],
    "development": ["infrastructure", "education", "healthcare", "agriculture", "innovation", "development", "progress", "growth", "economy"],
    "technology": ["technology", "tech", "ai", "artificial intelligence", "digital", "internet", "software", "cyber"],
    "social": ["society", "community", "people", "welfare", "help", "support", "youth", "women"]
}

def calculate_rule_based_score(keywords: list, entities: dict, language: str) -> dict:
    score = 0.0
    matched_groups = []
    matched_keywords = []
    
    entity_values = [item for sublist in entities.values() for item in sublist]
    text_to_check = " ".join(keywords).lower() + " " + " ".join(entity_values).lower()
    
    for group_name, group_keywords in KEYWORD_GROUPS.items():
        group_matched = False
        for kw in group_keywords:
            if kw in text_to_check:
                group_matched = True
                if kw not in matched_keywords:
                    matched_keywords.append(kw)
        
        if group_matched:
            score += 25.0  # 25 points per matched group, max 100
            matched_groups.append(group_name)
            
    return {
        "overall_score": round(min(100.0, score), 2),
        "matched_groups": matched_groups,
        "matched_keywords": matched_keywords
    }