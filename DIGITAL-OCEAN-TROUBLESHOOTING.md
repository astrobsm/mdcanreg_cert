# Digital Ocean App Platform Troubleshooting

If you're still encountering the `$PORT` error and health check failures, follow these steps as a last resort:

## Option 1: Redeploy with Existing Changes

1. Go to your App Platform dashboard
2. Click on "Undeployed changes: Your live deployment and app spec are out of sync. View and redeploy changes"
3. Redeploy the application
4. Check the logs immediately after deployment

## Option 2: Use the Ultra-Simple Deployment

If Option 1 fails, try this ultra-minimal approach:

1. Rename `Dockerfile.basic` to `Dockerfile` (or create a new app with Dockerfile.basic as the Dockerfile)
2. Push the changes to GitHub
3. Create a new app on Digital Ocean using this repository
4. Let Digital Ocean detect the Dockerfile automatically
5. Deploy without specifying custom build or run commands

## Option 3: Use Custom Commands

If both approaches above fail, try using explicit custom commands:

1. Build command: `pip install flask gunicorn`
2. Run command: `gunicorn --bind 0.0.0.0:8080 basic_app:app`

## Important Notes:

1. Digital Ocean App Platform requires your app to bind to port 8080
2. The `$PORT` environment variable sometimes has issues with shell expansion
3. Using a fixed port (8080) is the most reliable approach
4. Health checks require a working endpoint (usually `/` or `/health`)
5. Deployment can take a few minutes - be patient and check the logs

## After Deployment

Once your basic app is successfully deployed, you can gradually add more functionality to ensure everything works properly.

Remember: Your application environment variables (DATABASE_URL, EMAIL settings, etc.) are correctly configured in your App Platform dashboard - they'll be available to your application when it runs.
