# Pushing the MDCAN BDM 2025 Certificate Platform to a Remote Repository

This guide will help you push the local repository to a remote server like GitHub, GitLab, or Bitbucket.

## Prerequisites

1. A GitHub, GitLab, or Bitbucket account
2. Git installed on your local machine
3. The local repository already initialized and committed (this has been done)

## Step 1: Create a new repository on your Git hosting service

1. Log in to your GitHub/GitLab/Bitbucket account
2. Create a new repository (e.g., "mdcan-bdm-2025-certificate")
3. Do not initialize it with a README, .gitignore, or license
4. Copy the repository URL (e.g., `https://github.com/username/mdcan-bdm-2025-certificate.git`)

## Step 2: Add the remote repository to your local repository

Open a terminal in the project directory and run:

```bash
git remote add origin YOUR_REMOTE_REPOSITORY_URL
```

Replace `YOUR_REMOTE_REPOSITORY_URL` with the URL you copied in Step 1.

## Step 3: Push your local repository to the remote server

```bash
git push -u origin master
```

If you're using GitHub and want to use `main` as the default branch instead of `master`:

```bash
git branch -M main
git push -u origin main
```

## Step 4: Verify the push was successful

1. Visit your repository on the Git hosting service
2. You should see all the files that were committed

## Additional Information

### Repository Structure

The repository contains the following key components:

- Frontend: React.js application for the web interface
- Backend: Flask API for certificate generation and database operations
- Database scripts: SQL scripts for setting up and migrating the PostgreSQL database
- Deployment files: Docker configurations and deployment guides for various platforms
- Documentation: Various guides for setup, testing, and troubleshooting

### Deployment

After pushing to the remote repository, you can follow the instructions in the `DIGITAL-OCEAN-DEPLOYMENT.md` file to deploy the application to Digital Ocean.

### Future Updates

When making future changes:

1. Pull the latest changes: `git pull origin master`
2. Make your changes
3. Commit your changes: `git add . && git commit -m "Description of changes"`
4. Push to the remote repository: `git push origin master`
