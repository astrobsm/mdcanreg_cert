# Digital Ocean Deployment Guide for MDCAN BDM 2025 Certificate Platform

This guide provides step-by-step instructions for deploying the MDCAN BDM 2025 Certificate Platform on Digital Ocean.

## Prerequisites

1. A Digital Ocean account
2. Domain name (optional, but recommended)
3. Docker and Docker Compose installed on your local machine (for testing)

## Deployment Options

### Option 1: Deploy using App Platform (Recommended)

Digital Ocean's App Platform provides the simplest way to deploy the application.

1. **Prepare your repository**:
   - Push your code to a GitHub repository
   - Ensure your repository includes the `Dockerfile` provided

2. **Create a new App on Digital Ocean**:
   - Log in to your Digital Ocean account
   - Go to "Apps" and click "Create App"
   - Select "GitHub" as the source
   - Select your repository and branch
   - Digital Ocean will automatically detect the Dockerfile

3. **Configure your app**:
   - Set the following environment variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `EMAIL_HOST`: SMTP server for sending emails
     - `EMAIL_PORT`: SMTP port
     - `EMAIL_USER`: SMTP username
     - `EMAIL_PASSWORD`: SMTP password
     - `EMAIL_FROM`: From address for sent emails

4. **Configure database**:
   - Add a PostgreSQL database from the Resources tab
   - Digital Ocean will automatically add the connection string to your environment

5. **Deploy the application**:
   - Click "Deploy to Production"
   - Wait for the build and deployment to complete

### Option 2: Deploy using Droplets and Docker

For more control over your server environment, you can use Digital Ocean Droplets.

1. **Create a Droplet**:
   - Log in to your Digital Ocean account
   - Create a new Droplet
   - Select Ubuntu 20.04 LTS
   - Choose a plan (Basic, starting at $5/month should work for testing)
   - Select a datacenter region close to your users
   - Add your SSH key
   - Click "Create Droplet"

2. **Set up the server**:
   - SSH into your Droplet: `ssh root@your_droplet_ip`
   - Update packages: `apt update && apt upgrade -y`
   - Install Docker: `apt install docker.io docker-compose -y`
   - Enable Docker service: `systemctl enable --now docker`

3. **Deploy the application**:
   - Clone your repository: `git clone https://github.com/yourusername/mdcan-bdm-certificate.git`
   - Navigate to the project directory: `cd mdcan-bdm-certificate`
   - Create a `.env` file with your environment variables:
     ```
     DATABASE_URL=postgresql://username:password@host:port/dbname
     EMAIL_HOST=smtp.example.com
     EMAIL_PORT=587
     EMAIL_USER=your_email@example.com
     EMAIL_PASSWORD=your_password
     EMAIL_FROM=MDCAN BDM 2025 <your_email@example.com>
     ```
   - Build and run the Docker container:
     ```
     docker build -t mdcan-certificate .
     docker run -d -p 80:8080 --env-file .env --name mdcan mdcan-certificate
     ```

4. **Set up a domain name (optional)**:
   - Add an A record in your domain's DNS settings pointing to your Droplet's IP address
   - Install Nginx to handle HTTPS:
     ```
     apt install nginx certbot python3-certbot-nginx -y
     ```
   - Configure Nginx as a reverse proxy:
     ```
     nano /etc/nginx/sites-available/mdcan
     ```
     Add the following configuration:
     ```
     server {
         listen 80;
         server_name yourdomain.com;
         
         location / {
             proxy_pass http://localhost:8080;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```
   - Enable the site:
     ```
     ln -s /etc/nginx/sites-available/mdcan /etc/nginx/sites-enabled/
     nginx -t
     systemctl restart nginx
     ```
   - Set up HTTPS:
     ```
     certbot --nginx -d yourdomain.com
     ```

## Database Management

### Creating the PostgreSQL Database

1. **Create a managed database**:
   - Go to "Databases" in your Digital Ocean dashboard
   - Click "Create Database Cluster"
   - Select PostgreSQL
   - Choose a plan
   - Select a datacenter region
   - Click "Create Database Cluster"

2. **Connect to your database**:
   - After creation, navigate to the database cluster
   - Note the connection details
   - Use the connection string in your app's environment variables

3. **Initialize the database**:
   - Connect to your database using a PostgreSQL client
   - Run the schema creation scripts from `backend/create_comprehensive_database.sql`

## Monitoring and Maintenance

1. **Monitor application logs**:
   - View container logs: `docker logs mdcan`
   - Set up logging to a service like Papertrail or Loggly for production

2. **Monitor system resources**:
   - Install the Digital Ocean Agent for server monitoring
   - Set up alerts for high CPU, memory usage, or disk space

3. **Regular backups**:
   - Enable automated backups for your database
   - Set up a cronjob to backup any uploaded files

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Verify connection string is correct
   - Check if the database server is accessible from your app

2. **Email sending fails**:
   - Verify SMTP credentials
   - Check if the SMTP server allows connections from your app server

3. **Certificate generation issues**:
   - Check if wkhtmltopdf is installed correctly
   - Verify file permissions for temporary directories

For additional support, consult the project documentation or contact the development team.
