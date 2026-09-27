# ProofLoop — Live Deployment Guide

This guide explains how to deploy ProofLoop to get a public live link for your hackathon submission.

---

## Recommended Options at a Glance

| Provider | Type | Setup Time | URL Format | Recommended For |
|---|---|---|---|---|
| **Vercel** | Global Static CDN | **60 seconds** | `https://proofloop.vercel.app` | **Best & fastest for hackathon submission links** |
| **Render** | Cloud Python Service | **3 minutes** | `https://proofloop.onrender.com` | If you want the full Python server running online |
| **GitHub Pages** | GitHub Built-in | **2 minutes** | `https://<user>.github.io/IBMBOB/` | Native zero-dependency GitHub hosting |
| **Localtunnel** | Instant Tunnel | **10 seconds** | `https://xxxx.loca.lt` | Instant demo link while testing locally |

---

## Option 1: Vercel (Recommended — 1 Minute)

The repository includes a ready-to-use [`vercel.json`](file:///Users/shalem/IBMBOB/vercel.json) configuration.

### Steps:
1. Commit and push your latest changes to GitHub:
   ```bash
   git add .
   git commit -m "Add deployment configs and dashboard"
   git push origin main
   ```
2. Open **[vercel.com/new](https://vercel.com/new)** and sign in with GitHub.
3. Import the repository **`Alexprinse/IBMBOB`**.
4. Leave all build settings as default (Vercel automatically detects `vercel.json`).
5. Click **Deploy**.
6. You will receive an instant public HTTPS link, e.g.:
   ```text
   https://proofloop-alexprinse.vercel.app
   ```

---

## Option 2: Render.com (Full Python Web Service — Free)

The repository includes [`Procfile`](file:///Users/shalem/IBMBOB/Procfile) and [`render.yaml`](file:///Users/shalem/IBMBOB/render.yaml).

### Steps:
1. Push your code to GitHub.
2. Go to **[dashboard.render.com](https://dashboard.render.com)** $\to$ **New +** $\to$ **Web Service**.
3. Connect your repository **`Alexprinse/IBMBOB`**.
4. Configure settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `python dashboard/serve.py --port $PORT`
5. Select the **Free** tier and click **Create Web Service**.
6. Render will build and deploy, giving you a live URL:
   ```text
   https://proofloop.onrender.com
   ```

---

## Option 3: GitHub Pages (Built into GitHub)

### Steps:
1. Go to your GitHub repository: **`https://github.com/Alexprinse/IBMBOB`**.
2. Click **Settings** $\to$ **Pages** (in the left sidebar).
3. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main`, Folder: `/ (root)`
4. Click **Save**.
5. After 1–2 minutes, your live site will be live at:
   ```text
   https://alexprinse.github.io/IBMBOB/dashboard/
   ```

---

## Option 4: Instant Public Link Right Now (Localtunnel)

If you need a public URL immediately to share with teammates or test on your phone:

1. Ensure the dashboard server is running locally:
   ```bash
   python dashboard/serve.py --port 8080
   ```
2. In a second terminal window, run:
   ```bash
   npx localtunnel --port 8080 --subdomain proofloop-demo
   ```
3. You will get an instant public URL:
   ```text
   https://proofloop-demo.loca.lt
   ```

