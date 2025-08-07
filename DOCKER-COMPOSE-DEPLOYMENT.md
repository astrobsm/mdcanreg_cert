# Digital Ocean Deployment Guide for MDCAN BDM 2025 Certificate Platform

This guide provides step-by-step instructions for deploying the MDCAN BDM 2025 Certificate platform on a Digital Ocean Droplet using Docker Compose.

## Prerequisites

1. A Digital Ocean account
2. SSH key pair for secure access
3. Docker and Docker Compose installed on your local machine
4. Git installed on your local machine

## Step 1: Create a Digital Ocean Droplet

1. Log in to your Digital Ocean account
2. Click "Create" and select "Droplets"
3. Choose Ubuntu 20.04 (LTS) x64
4. Select a plan with at least 2GB RAM
5. Choose a datacenter region close to your target audience (e.g., New York or London)
6. Add your SSH key or create a new one
7. Name your Droplet (e.g., mdcan-bdm-2025)
8. Click "Create Droplet"

## Step 2: Set Up the Droplet

1. Once your Droplet is created, note its IP address
2. SSH into your Droplet:
   ```
   ssh root@your-droplet-ip
   ```

3. Update packages and install Docker and Docker Compose:
   ```
   apt update
   apt upgrade -y
   apt install -y apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   apt update
   apt install -y docker-ce
   systemctl status docker
   
   # Install Docker Compose
   curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   docker-compose --version
   ```

## Step 3: Clone the Repository and Prepare Environment Variables

1. Clone your repository to the Droplet:
   ```
   git clone https://github.com/your-username/mdcan-bdm-2025.git
   cd mdcan-bdm-2025
   ```

2. Create a `.env` file for environment variables:
   ```
   nano .env
   ```

3. Add the following environment variables:
   ```
   DB_USER=postgres
   DB_PASSWORD=your_strong_password
   DB_NAME=mdcan042_db
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_FROM=MDCAN BDM 2025 <your-email@gmail.com>
   ```

4. Save and exit (Ctrl+X, then Y, then Enter)

## Step 4: Deploy with Docker Compose

1. Deploy using Docker Compose:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. Check if the containers are running:
   ```
   docker-compose -f docker-compose.prod.yml ps
   ```

3. Check the logs if needed:
   ```
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Step 5: Set Up Nginx for SSL and Domain (Optional)

1. Install Nginx:
   ```
   apt install -y nginx
   ```

2. Create an Nginx configuration file:
   ```
   nano /etc/nginx/sites-available/mdcan-bdm
   ```

3. Add the following configuration (replace with your domain):
   ```
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. Enable the site:
   ```
   ln -s /etc/nginx/sites-available/mdcan-bdm /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

5. Set up SSL with Certbot:
   ```
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## Step 6: Set Up Automatic Updates (Optional)

1. Create a script for automatic updates:
   ```
   nano /root/update-mdcan.sh
   ```

2. Add the following content:
   ```bash
   #!/bin/bash
   cd /root/mdcan-bdm-2025
   git pull
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Make the script executable:
   ```
   chmod +x /root/update-mdcan.sh
   ```

4. Set up a cron job to run the script weekly:
   ```
   crontab -e
   ```

5. Add the following line:
   ```
   0 0 * * 0 /root/update-mdcan.sh >> /var/log/mdcan-update.log 2>&1
   ```

## Step 7: Monitoring and Maintenance

1. Set up basic monitoring with Docker stats:
   ```
   docker stats
   ```

2. Check disk usage:
   ```
   df -h
   ```

3. Monitor the application logs:
   ```
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Backup and Restore

### Database Backup
```
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres mdcan042_db > backup_$(date +%Y%m%d%H%M%S).sql
```

### Database Restore
```
cat backup_file.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres mdcan042_db
```

## Troubleshooting

1. If the application is not accessible, check:
   - Docker container status: `docker ps`
   - Application logs: `docker-compose -f docker-compose.prod.yml logs app`
   - Database logs: `docker-compose -f docker-compose.prod.yml logs postgres`
   - Nginx configuration: `nginx -t`
   - Firewall settings: `ufw status`

2. If emails are not being sent:
   - Check email configuration in the .env file
   - Verify that the Gmail account is set up for app passwords
   - Check application logs for email-related errors

3. If certificate generation fails:
   - Verify that wkhtmltopdf is installed correctly
   - Check application logs for PDF generation errors
   - Ensure the certificate templates are accessible to the application

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Digital Ocean Documentation](https://docs.digitalocean.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt/Certbot](https://certbot.eff.org/)
