
import re
import langid

positive_words = {"gracias","love","rico","delicioso","excelente","increíble","amazing","great","awesome","fantástico","sabroso"}
negative_words = {"malo","frío","tarde","caro","horrible","terrible","pésimo","bad","awful","cold","late","dirty","wrong"}
question_marks = re.compile(r"\?\s*$")

def detect_lang(text: str) -> str:
    try:
        lang, _ = langid.classify(text or "")
        return "es" if lang.startswith("es") else "en"
    except Exception:
        return "en"

def classify(text: str) -> str:
    t = (text or "").lower()
    if "?" in t or question_marks.search(t):
        return "question"
    if any(w in t for w in negative_words):
        return "negative"
    if any(w in t for w in positive_words):
        return "positive"
    return "neutral"
