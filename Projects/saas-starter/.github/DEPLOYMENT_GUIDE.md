# Production Deployment Guide

Follow the **Production Deployment Checklist** in [README.md](../README.md#-production-deployment-checklist) first.

## Quick Deploy on Popular Platforms

### 1. Railway (Recommended for SaaS)

Best for: Fastest setup, automatic deploys from Git

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set SECRET_KEY="your-strong-key"
railway variables set DEBUG="False"
railway variables set DATABASE_URL="$DATABASE_URL"  # Auto-linked to Postgres
railway variables set STRIPE_SECRET_KEY="sk_live_..."
railway variables set STRIPE_PUBLIC_KEY="pk_live_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PRICE_ID="price_..."
railway variables set ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# Deploy
railway up

# Run migrations
railway run python manage.py migrate

# Collect static
railway run python manage.py collectstatic --noinput

# Check health
curl https://your-railway-domain.com/health/
```

### 2. Heroku

Best for: Mature platform, easy for teams

```bash
# Install Heroku CLI
npm i -g heroku

# Login
heroku login

# Create app
heroku create your-saas-app

# Add Postgres (free tier ended, but available)
heroku addons:create heroku-postgresql:standard-0

# Set config vars
heroku config:set SECRET_KEY="your-strong-key" --app your-saas-app
heroku config:set DEBUG=False --app your-saas-app
heroku config:set STRIPE_SECRET_KEY="sk_live_..." --app your-saas-app
# ... (set other STRIPE_* vars)

# Deploy
git push heroku main

# Run migrations automatically (check Procfile includes release command)
# Heroku runs `release` phase before each deployment

# Check logs
heroku logs --tail --app your-saas-app
```

### 3. Render

Best for: Docker-native, simple UI

```bash
# 1. Push code to GitHub

# 2. Go to https://dashboard.render.com
# 3. New → Web Service → Connect GitHub repo

# 4. Configure:
#    - Build command: pip install -r backend/requirements.txt
#    - Start command: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:8000

# 5. Add environment variables in Render Dashboard:
#    - SECRET_KEY
#    - DEBUG=False
#    - DATABASE_URL (link to Postgres)
#    - STRIPE_* keys
#    - ALLOWED_HOSTS

# 6. Deploy (automatic or manual trigger)

# Run migrations via Render Shell:
# Dashboard → Web Service → Shell → python backend/manage.py migrate
```

### 4. Docker + AWS ECS / Fargate

Best for: Custom infrastructure, scaling

```bash
# 1. Build Docker image locally
docker build -t saas-app:latest backend/

# 2. Push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag saas-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/saas-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/saas-app:latest

# 3. Create ECS task definition (JSON) with env vars for production

# 4. Create ECS service, load balancer, RDS Postgres

# 5. Run migrations (one-off task):
aws ecs run-task --cluster prod-cluster --task-definition saas-app --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}" \
  --overrides '{"containerOverrides":[{"name":"app","command":["python","manage.py","migrate"]}]}'
```

### 5. Self-Hosted (VPS like DigitalOcean, Linode, Vultr)

Best for: Full control, lowest cost at scale

```bash
# 1. SSH into your VPS
ssh root@your-server-ip

# 2. Install dependencies
apt-get update && apt-get install -y python3.11 python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx git

# 3. Clone repository
git clone https://github.com/yourusername/saas-project.git
cd saas-project/backend

# 4. Create virtualenv
python3.11 -m venv .venv
source .venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Create .env file (keep SECRET_KEY, DB credentials secure)
nano .env
# SECRET_KEY=your-strong-key
# DEBUG=False
# DATABASE_URL=postgresql://appuser:password@localhost/appdb
# STRIPE_*=...

# 7. Create Postgres user and database
sudo -u postgres createuser appuser
sudo -u postgres createdb appdb -O appuser

# 8. Run migrations
python manage.py migrate

# 9. Collect static
python manage.py collectstatic --noinput

# 10. Setup gunicorn systemd service
sudo nano /etc/systemd/system/saas-app.service
# [Unit]
# Description=SaaS Django App
# After=network.target
#
# [Service]
# User=appuser
# WorkingDirectory=/home/appuser/saas-project/backend
# ExecStart=/home/appuser/saas-project/backend/.venv/bin/gunicorn config.wsgi:application --workers 3 --bind unix:saas-app.sock
# Restart=always
# RestartSec=10
# StandardOutput=append:/var/log/saas-app.log
# StandardError=append:/var/log/saas-app-error.log
#
# [Install]
# WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl start saas-app
sudo systemctl enable saas-app

# 11. Setup nginx
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/saas-app
# Edit with your domain
sudo ln -s /etc/nginx/sites-available/saas-app /etc/nginx/sites-enabled/

# 12. Setup TLS with certbot
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# 13. Reload nginx
sudo systemctl reload nginx

# 14. Monitor
tail -f /var/log/saas-app.log
```

---

## Post-Deployment Checklist

- [ ] Health check passes: `curl https://yourdomain.com/health/`
- [ ] Stripe webhooks pointing to `/billing/webhooks/stripe/`
- [ ] Logs show no errors
- [ ] Test signup → payment → subscription activation
- [ ] Test subscription cancellation
- [ ] Verify static files served (CSS/JS loaded)
- [ ] Setup monitoring (Sentry / Pingdom)
- [ ] Configure automated backups
- [ ] Add custom domain (DNS CNAME / A records)
- [ ] Setup email notifications (SMTP if needed)

---

## Rollback Strategy

If something goes wrong:

- **Heroku/Railway:** `git revert <commit-hash> && git push` (redeploy previous version)
- **Docker:** `docker run -it <previous-image-id>` or update service to previous tag
- **Database:** Restore from snapshot/backup

---

## Monitoring & Alerts

Setup alerts for:

- App crashes (Sentry / platform-native)
- Database errors
- Payment failures
- Uptime (Pingdom, Uptime Robot)
- Disk space / memory
