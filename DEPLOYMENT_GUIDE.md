# 🚀 Deployment Guide: Production & Development Setup

This guide provides instructions for deploying the **AI Influencer Discovery & Analytics Dashboard** on local development servers, Linux VPS instances (Ubuntu/Debian), and cloud production environments.

---

## 📋 Prerequisites
- **Operating System**: Linux (Ubuntu 22.04 LTS recommended), macOS, or Windows
- **Python Version**: Python `3.10+` or `3.12`
- **Database Engine**: PostgreSQL `15+`
- **Web Server**: Gunicorn `23.0.0` + Nginx
- **API Access**: Active OpenRouter API Key

---

## ⚙️ Step-by-Step Installation

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/SharmaVaibhav976531/AI-Influencer.git
cd AI_Influence_Dashboard

python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies & spaCy Model
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables
Create `.env` in the root folder:
```ini
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/ai_influencer_db
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
OPENROUTER_MODEL_NAME=nvidia/nemotron-3-ultra-550b-a55b:free
```

### 4. Database Setup & Migrations
```bash
# Apply Django migrations
python manage.py migrate

# Create Administrative Superuser
python manage.py createsuperuser
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🌐 Production Server Setup (Gunicorn + Nginx)

### Gunicorn Systemd Service Config (`/etc/systemd/system/gunicorn.service`)
```ini
[Unit]
Description=gunicorn daemon for AI Influencer Dashboard
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/AI_Influence_Dashboard
ExecStart=/home/ubuntu/AI_Influence_Dashboard/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ubuntu/AI_Influence_Dashboard/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy Config (`/etc/nginx/sites-available/ai_influencer`)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /home/ubuntu/AI_Influence_Dashboard/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/AI_Influence_Dashboard/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/AI_Influence_Dashboard/gunicorn.sock;
    }
}
```

---

## 🔧 Troubleshooting Common Deployment Issues

| Issue | Root Cause | Solution |
|---|---|---|
| `spaCy model missing` | `en_core_web_sm` model package not downloaded | Run `python -m spacy download en_core_web_sm` |
| `CSRF verification failed (403)` | Domain missing from `CSRF_TRUSTED_ORIGINS` | Add `CSRF_TRUSTED_ORIGINS=https://yourdomain.com` in `.env` |
| `PostgreSQL Connection Refused` | PostgreSQL service inactive or incorrect port | Check `sudo systemctl status postgresql` and verify `DATABASE_URL` credentials |
