set up the project

run it locally

deploy to EC2

update using CI/CD

restart services

debug common issues

# Clone the Project
git clone https://github.com/x24250511/Incident_MSystem.git
cd Incident_MSystem

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Requirements
pip install -r requirements.txt

# Run Database Migrations
python manage.py migrate

# Create Superuser
python manage.py createsuperuser

#Run the Project Locally
python manage.py runserver (runs at: http://127.0.0.1:8000)

# AWS EC2 Deployment Guide
This assumes:
Ubuntu 24.04
Nginx installed
Python 3.12
Gunicorn
SSH key-based login

# GitHub Actions auto-deploy
Update and Install Basics
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx git -y

# Clone the Project on EC2
git clone https://github.com/x24250511/Incident_MSystem.git ims
cd ims

# Create Virtual Environment on EC2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set Environment Variables
Edit:
sudo nano /etc/environment

Add:
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=your-public-ip

# Reload:
source /etc/environment

# Collect Static Files
python manage.py collectstatic

# Configure Gunicorn (systemd)
Create the service:
sudo nano /etc/systemd/system/gunicorn.service
Paste:
[Unit]
Description=Gunicorn for IMS
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/ims

ExecStart=/home/ubuntu/ims/venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/home/ubuntu/ims/gunicorn.sock \
  Incident_MSystem.wsgi:application

EnvironmentFile=/etc/environment
Restart=always
UMask=007

[Install]
WantedBy=multi-user.target


# Inside Bash Enable:
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn

# Configure Nginx Reverse Proxy
sudo nano /etc/nginx/sites-available/ims
Paste
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location /static/ {
        alias /home/ubuntu/ims/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/ims/gunicorn.sock;
    }
}

# Enable site:
sudo ln -s /etc/nginx/sites-available/ims /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# CI/CD Deployment with GitHub Actions
Your deployment workflow lives at:
.github/workflows/deploy.yml

# Push to main triggers:
flake8 style check
bandit security scan
scp upload to EC2
restart gunicorn
reload nginx

# To deploy, just run:
git add .
git commit -m "update"
git push

# Manual Deployment After Changes (Optional)
If you don’t want to wait for CI/CD:
ssh -i <your-key.pem> ubuntu@<public-ip>
cd ims
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Useful Commands
Check gunicorn logs
sudo journalctl -u gunicorn -n 100 --no-pager

# Check nginx logs
sudo tail -n 100 /var/log/nginx/error.log

Restart Services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

Check running processes
ps aux | grep gunicorn

# Common Fixes
# 502 Bad Gateway
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo journalctl -u gunicorn -n 50

Permission denied on socket
sudo chown ubuntu:www-data /home/ubuntu/ims/gunicorn.sock
sudo chmod 777 /home/ubuntu/ims/gunicorn.sock

DisallowedHost

Add IP to /etc/environment:

DJANGO_ALLOWED_HOSTS=your-ip


