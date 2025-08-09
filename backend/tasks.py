
from celery import Celery
import time
from config import Config
from db import SessionLocal
from models import Comment, Reply
from facebook import send_comment_reply

celery = Celery(__name__, broker=Config.REDIS_URL, backend=Config.REDIS_URL)

@celery.task
def enqueue_send_reply(comment_db_id: int):
    time.sleep(Config.RESPONSE_DELAY_SECONDS)
    db = SessionLocal()
    try:
        comment = db.query(Comment).where(Comment.id == comment_db_id).one_or_none()
        if not comment:
            return
        reply = db.query(Reply).where(Reply.comment_id == comment.id).order_by(Reply.id.desc()).first()
        if not reply or reply.sent is True:
            return
        if comment.status not in ("approved","sent") and reply.approved is not True:
            return
        res = send_comment_reply(comment.platform_id, reply.generated_text)
        reply.sent = True
        comment.status = "sent"
        db.add(reply); db.add(comment); db.commit()
        return res
    except Exception as e:
        if 'reply' in locals():
            reply.error = str(e)
            db.add(reply); db.commit()
        raise
    finally:
        db.close()
