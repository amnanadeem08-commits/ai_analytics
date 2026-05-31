# DataBot AI — GitHub Pages website

## Website name (brand)

**DataBot AI** — AI bots, dashboards & automation by Amna Malik

## Your live URL (after enabling GitHub Pages)

**https://amnanadeem08-commits.github.io/ai_analytics/**

This is a normal static website on GitHub Pages — not Streamlit.

## Fix 404 — enable GitHub Pages (pick ONE method)

Your site shows **404** until you turn Pages on in GitHub Settings.

### Method A — Easiest (recommended): `/docs` folder

1. Open **Settings → Pages**:  
   https://github.com/amnanadeem08-commits/ai_analytics/settings/pages
2. **Build and deployment** → **Source**: **Deploy from a branch**
3. **Branch**: `main` (or `master`) → **Folder**: `/docs` → **Save**
4. Wait 1–2 minutes, then open:  
   https://amnanadeem08-commits.github.io/ai_analytics/

The built site lives in the `docs/` folder (updated when you run `npm run build` and copy to `docs/`).

### Method B — GitHub Actions (automatic on push)

1. Same **Settings → Pages** link as above
2. **Source**: **GitHub Actions**
3. Re-run the workflow:  
   https://github.com/amnanadeem08-commits/ai_analytics/actions/workflows/deploy-website.yml  
   → latest run → **Re-run all jobs**

## Local preview

```bash
cd ai-services-web
npm install
npm run dev
```

## Optional: shorter URL

Create a new repo named `databot-ai` on GitHub, then your URL becomes:

**https://amnanadeem08-commits.github.io/databot-ai/**

Or rename your profile repo to `amnanadeem08-commits.github.io` for:

**https://amnanadeem08-commits.github.io/**
