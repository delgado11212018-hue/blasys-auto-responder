
import hmac, hashlib, requests
from flask import Blueprint, request, abort
from config import Config
from db import SessionLocal
from models import Comment, Person, Reply
from ai import generate_reply
from tasks import enqueue_send_reply

bp = Blueprint("facebook", __name__)

def verify_signature(req):
    signature = req.headers.get("X-Hub-Signature-256", "")
    if not signature or not Config.FACEBOOK_APP_SECRET:
        return True  # allow in dev
    try:
        algo, sig = signature.split("=")
    except ValueError:
        return False
    mac = hmac.new(Config.FACEBOOK_APP_SECRET.encode(), msg=req.data, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), sig)

@bp.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == Config.FACEBOOK_VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@bp.post("/webhook")
def webhook():
    if not verify_signature(request):
        abort(403)
    payload = request.get_json(force=True, silent=True) or {}
    entries = payload.get("entry", [])
    db = SessionLocal()
    try:
        for entry in entries:
            for ch in entry.get("changes", []):
                if ch.get("field") != "comments":
                    continue
                val = ch.get("value", {})
                comment_id = val.get("comment_id")
                post_id = val.get("post_id")
                from_ = val.get("from", {})
                user_id = str(from_.get("id", ""))
                username = (from_.get("username") or from_.get("name") or "user").lower()
                message = val.get("message", "")

                # upsert person
                person = db.query(Person).filter_by(platform_user_id=user_id).one_or_none()
                if not person:
                    person = Person(platform_user_id=user_id, username=username)
                    person.is_influencer = username in Config.INFLUENCER_USERNAMES
                    person.is_repeat_customer = username in Config.REPEAT_CUSTOMER_NAMES
                    db.add(person); db.flush()

                # skip duplicates
                existing = db.query(Comment).filter_by(platform_id=comment_id).one_or_none()
                if existing:
                    continue

                reply_text, sentiment, lang, personalized = generate_reply(message, username, person.is_influencer, person.is_repeat_customer)

                c = Comment(platform_id=comment_id, post_id=post_id, user_id=user_id,
                            username=username, text=message, sentiment=sentiment, lang=lang, personalized=personalized,
                            status="pending")
                db.add(c); db.flush()
                r = Reply(comment_id=c.id, generated_text=reply_text, approved=False, sent=False)
                db.add(r); db.commit()

                auto_ok = (sentiment == "positive" and Config.AUTO_SEND_POSITIVE) or \
                          (sentiment == "question" and Config.AUTO_SEND_QUESTIONS) or \
                          (sentiment == "negative" and Config.AUTO_SEND_NEGATIVE)

                if auto_ok:
                    enqueue_send_reply.delay(c.id)
        return "ok", 200
    finally:
        db.close()

def send_comment_reply(platform_comment_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{platform_comment_id}/replies"
    params = {"message": message, "access_token": Config.FACEBOOK_PAGE_ACCESS_TOKEN}
    resp = requests.post(url, data=params, timeout=15)
    if resp.status_code >= 400:
        raise RuntimeError(f"Graph error: {resp.status_code} {resp.text}")
    return resp.json()
