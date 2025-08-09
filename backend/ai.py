
from config import Config
from templates import pick_template
from classify import detect_lang, classify as rule_classify

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def generate_reply(text: str, username: str, is_influencer: bool, is_repeat: bool):
    lang = detect_lang(text)
    sentiment = rule_classify(text)
    personalized = is_influencer or is_repeat or username.lower() in Config.INFLUENCER_USERNAMES

    if not Config.OPENAI_API_KEY or OpenAI is None:
        msg = pick_template(sentiment, personalized, lang, is_influencer, is_repeat)
        return msg, sentiment, lang, personalized

    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    system = f"You are the social voice for {Config.BRAND_NAME}. Tone: {Config.BRAND_TONE}. Respond in {lang}."
    user = (
        "Comment: " + text + "\n"
        "User: " + username + "\n"
        f"Audience flags: influencer={is_influencer}, repeat_customer={is_repeat}\n"
        "Constraints:\n"
        "- One short reply (max 280 chars)\n"
        "- Never ask for private info in public; move sensitive details to DM\n"
        "- No emojis unless the comment used them\n"
        "- Keep it warm, professional, brand-safe\n"
    )

    completion = client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.4,
        max_tokens=120,
    )
    reply = completion.choices[0].message.content.strip()
    return reply, sentiment, lang, personalized
