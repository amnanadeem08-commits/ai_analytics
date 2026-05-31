# AI Services Web — SaaS marketing site

Modern React + Vite landing page for **Amna Malik** AI analytics services.

## Stack

- React 18 + Vite 5
- Tailwind CSS 3
- Vanilla JS scroll animations (no heavy animation libs — Lighthouse-friendly)

## Run locally

```bash
cd ai-services-web
npm install
npm run dev
```

Open http://localhost:5173

## Production build

```bash
npm run build
npm run preview
```

Deploy the `dist/` folder to Vercel, Netlify, GitHub Pages, or Cloudflare Pages.

## Structure

```
src/
├── components/
│   ├── layout/     Navbar, Footer
│   ├── sections/   Hero, PainPoints, Services, BotShowcase, DemoCards, Pricing, Testimonials, Contact
│   └── ui/         Button, Card, SectionHeader, AnimatedSection
├── data/content.js Centralized copy & links
├── hooks/useInView.js
├── App.jsx
└── main.jsx
```

## Sections

1. Hero — value prop + live demo CTAs
2. Pain points
3. Services — 4 offerings
4. Bot showcase — DataBot + Excel MVP
5. Demo cards — live Streamlit links
6. Pricing — 3 tiers
7. Testimonials / proof
8. Contact — mailto form

Edit all copy in `src/data/content.js`.
