
# Blasys Auto-Responder

End-to-end system to respond to Facebook/Instagram comments with a 5-minute delay, auto-send for positives/questions, and manual review for negatives. Personalizes for influencers and repeat customers. Tracks metrics.

## Quick Start

1) Install Docker & Docker Compose.
2) Copy `.env.example` to `.env` and fill secrets (Graph API tokens, etc.).
3) `docker compose up --build`
4) Visit http://localhost:8080 to view the admin.

### Webhook Setup (Facebook/Instagram)

- Set your Webhook callback URL to `https://YOUR_HOST/facebook/webhook`
- Verification token must match `FACEBOOK_VERIFY_TOKEN`.
- Subscribe `comments` field for your page/app.
- Grant `pages_read_engagement`, `pages_manage_metadata`, `pages_manage_posts`, `pages_manage_engagement`.

### Notes

- Queue: Celery + Redis.
- Storage: Postgres.
- Delay: `RESPONSE_DELAY_SECONDS` (default 300 seconds).
- Optional OpenAI for higher-quality replies; otherwise templates + rules are used.
