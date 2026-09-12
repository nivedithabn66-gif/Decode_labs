# DevLens Cloud Deployment Guide

This guide provides step-by-step instructions to deploy **DevLens** (FastAPI Backend + React Frontend + Supervised ML Classifier) to cloud platforms.

---

## Option 1: Render.com (Recommended for Free / Quick Hosting)

DevLens includes a pre-configured `render.yaml` file for 1-click cloud deployment.

### Steps:
1. Push your repository to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy DevLens to Cloud"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/DevLens.git
   git push -u origin main
   ```
2. Log into [Render.com](https://render.com).
3. Click **New +** -> **Blueprints**.
4. Connect your `DevLens` GitHub repository.
5. Render will automatically detect `render.yaml` and launch:
   - `devlens-backend` (FastAPI + ML Model on port 8000)
   - `devlens-frontend` (Nginx + React App)

---

## Option 2: AWS EC2 (Docker Compose Deployment)

For deploying to an AWS EC2 instance (Ubuntu 22.04 LTS):

### Steps:
1. Launch an AWS EC2 instance (t3.small or t3.medium recommended).
2. Open inbound security group ports: `80`, `443`, `8000`, `3000`.
3. SSH into your instance:
   ```bash
   ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```
4. Install Docker & Docker Compose:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
5. Clone your repository and start containers:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DevLens.git
   cd DevLens
   docker compose up -d --build
   ```
6. Access DevLens at `http://YOUR_EC2_PUBLIC_IP:3000`.

---

## Option 3: Google Cloud Run (Serverless Deployment)

### Deploy Backend to Cloud Run:
```bash
# 1. Build & push Docker image to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/devlens-backend:latest -f Dockerfile.backend .

# 2. Deploy backend service
gcloud run deploy devlens-backend \
  --image gcr.io/YOUR_PROJECT_ID/devlens-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Deploy Frontend to Cloud Run:
```bash
# 1. Build & push frontend image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/devlens-frontend:latest -f Dockerfile.frontend .

# 2. Deploy frontend service
gcloud run deploy devlens-frontend \
  --image gcr.io/YOUR_PROJECT_ID/devlens-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80
```

---

## Option 4: Vercel (Frontend) + Render (Backend)

1. **Deploy Backend to Render / Railway / Heroku**:
   - Create a Web Service pointing to `Dockerfile.backend`.
   - Copy your public backend URL (e.g. `https://devlens-backend.onrender.com`).

2. **Deploy Frontend to Vercel**:
   - Import your GitHub repo on [Vercel](https://vercel.com).
   - Set Root Directory to `frontend`.
   - Add Environment Variable:
     ```text
     VITE_API_BASE_URL=https://devlens-backend.onrender.com/api
     ```
   - Click **Deploy**.

---

## Local Production Container Test

Before pushing to the cloud, you can test the production build locally:

```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
