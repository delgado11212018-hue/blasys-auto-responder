
from flask import Flask, jsonify, request, send_from_directory
from config import Config
from db import init_db, SessionLocal
from models import Comment, Reply
from facebook import bp as facebook_bp
from tasks import enqueue_send_reply

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = Config.SECRET_KEY

init_db()
app.register_blueprint(facebook_bp, url_prefix="/facebook")

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/api/moderation/queue")
def moderation_queue():
    db = SessionLocal()
    try:
        items = db.query(Comment).where(Comment.status.in_(["new","pending"])).order_by(Comment.created_at.desc()).limit(200).all()
        out = []
        for c in items:
            r = db.query(Reply).where(Reply.comment_id==c.id).order_by(Reply.id.desc()).first()
            out.append({
                "id": c.id, "platform_id": c.platform_id, "username": c.username, "text": c.text,
                "sentiment": c.sentiment, "lang": c.lang, "personalized": c.personalized,
                "reply_id": r.id if r else None, "reply": r.generated_text if r else None,
                "status": c.status
            })
        return jsonify(out)
    finally:
        db.close()

@app.post("/api/moderation/approve")
def moderation_approve():
    payload = request.get_json(force=True)
    comment_id = int(payload.get("comment_id"))
    db = SessionLocal()
    try:
        c = db.query(Comment).where(Comment.id==comment_id).one_or_none()
        if not c: return jsonify(error="not found"), 404
        r = db.query(Reply).where(Reply.comment_id==c.id).order_by(Reply.id.desc()).first()
        if not r: return jsonify(error="no reply"), 400
        c.status = "approved"; r.approved = True
        db.add(c); db.add(r); db.commit()
        enqueue_send_reply.delay(c.id)
        return jsonify(ok=True)
    finally:
        db.close()

@app.post("/api/moderation/skip")
def moderation_skip():
    payload = request.get_json(force=True)
    comment_id = int(payload.get("comment_id"))
    db = SessionLocal()
    try:
        c = db.query(Comment).where(Comment.id==comment_id).one_or_none()
        if not c: return jsonify(error="not found"), 404
        c.status = "skipped"
        db.add(c); db.commit()
        return jsonify(ok=True)
    finally:
        db.close()

@app.get("/api/metrics")
def metrics():
    db = SessionLocal()
    try:
        total = db.query(Comment).count()
        sent = db.query(Comment).where(Comment.status=="sent").count()
        pending = db.query(Comment).where(Comment.status.in_(["new","pending","approved"])).count()
        negatives = db.query(Comment).where(Comment.sentiment=="negative").count()
        positives = db.query(Comment).where(Comment.sentiment=="positive").count()
        questions = db.query(Comment).where(Comment.sentiment=="question").count()
        return jsonify(dict(total=total, sent=sent, pending=pending, positives=positives, negatives=negatives, questions=questions))
    finally:
        db.close()

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
