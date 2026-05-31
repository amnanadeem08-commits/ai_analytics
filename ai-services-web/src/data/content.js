export const site = {
  name: "Amna Malik",
  brand: "DataBot AI",
  title: "Data & AI Engineer",
  email: "amnamalikk.007l@gmail.com",
  github: "https://github.com/amnanadeem08-commits",
  demos: {
    dataBot: "https://data-analytics-bot.streamlit.app/",
    excelBot: "https://excelmvp-muqntkjoq8527pxpxevcuj.streamlit.app/",
  },
};

export const navLinks = [
  { href: "#services", label: "Services" },
  { href: "#bots", label: "Bots" },
  { href: "#demos", label: "Demos" },
  { href: "#pricing", label: "Pricing" },
  { href: "#proof", label: "Proof" },
  { href: "#contact", label: "Contact" },
];

export const painPoints = [
  {
    icon: "⏳",
    title: "Hours lost in spreadsheets",
    body: "Manual cleaning, pivot tables, and chart building eat 80% of analyst time before any insight is delivered.",
  },
  {
    icon: "🔒",
    title: "Analyst bottleneck",
    body: "Business teams wait days for every question. Self-serve analytics never scales without the right tooling.",
  },
  {
    icon: "🧩",
    title: "Fragmented stack",
    body: "Excel, BI tools, Python notebooks, and slide decks live in silos — nothing tells the full story.",
  },
  {
    icon: "📉",
    title: "Charts without answers",
    body: "Dashboards show numbers but not the why, the risk, or the next action. Decisions still stall.",
  },
];

export const services = [
  {
    icon: "🤖",
    title: "AI Data Analyst Bot",
    tagline: "Upload → insights in seconds",
    bullets: [
      "Domain-aware KPIs across 10 business verticals",
      "NL→SQL, RAG Q&A, and executive summaries",
      "Branded PDF, PPTX, and Excel exports",
    ],
    cta: "View live demo",
    href: site.demos.dataBot,
  },
  {
    icon: "📗",
    title: "Excel Automation Bot",
    tagline: "Built for Fiverr & Upwork gigs",
    bullets: [
      "Auto-clean any Excel or CSV on upload",
      "Instant dashboards and AI business insights",
      "Client-ready reports in one click",
    ],
    cta: "Try Excel bot",
    href: site.demos.excelBot,
  },
  {
    icon: "📊",
    title: "Dashboard Services",
    tagline: "Custom Streamlit + Plotly builds",
    bullets: [
      "Cross-filter KPIs and executive view modes",
      "Map analysis and custom metric builder",
      "Hosted on Streamlit Cloud or your infra",
    ],
    cta: "Get a quote",
    href: "#contact",
  },
  {
    icon: "⚙️",
    title: "Custom AI Solutions",
    tagline: "Tailored automation & copilots",
    bullets: [
      "RAG knowledge bases on your documents",
      "Workflow bots for recurring client reports",
      "Integration with OpenAI, Claude, or OpenRouter",
    ],
    cta: "Discuss project",
    href: "#contact",
  },
];

export const bots = [
  {
    name: "DataBot AI v3.0",
    role: "Full analytics platform",
    features: ["Smart domain detection", "Cross-filter dashboards", "Data Story mode"],
    stack: ["Streamlit", "DuckDB", "FAISS", "Plotly"],
    demo: site.demos.dataBot,
    gradient: "from-accent/30 to-violet-500/20",
  },
  {
    name: "Excel MVP Bot",
    role: "Spreadsheet automation",
    features: ["One-click clean & chart", "AI executive summary", "Multi-format export"],
    stack: ["Python", "Pandas", "ReportLab", "pptx"],
    demo: site.demos.excelBot,
    gradient: "from-mint/20 to-accent/20",
  },
];

export const demos = [
  {
    title: "Data Analytics Bot",
    description: "Full AI platform with NL→SQL, map view, custom metrics, and branded exports.",
    image: "📈",
    href: site.demos.dataBot,
    stats: "10 domains · 8 modules",
  },
  {
    title: "Excel Automation MVP",
    description: "Upload Excel/CSV, get cleaned data, charts, and client-ready reports instantly.",
    image: "📗",
    href: site.demos.excelBot,
    stats: "Built for gig delivery",
  },
];

export const pricing = [
  {
    name: "Starter",
    price: "$30 – $200",
    period: "per Excel automation gig",
    description: "Perfect for Fiverr/Upwork one-off jobs.",
    features: [
      "Excel/CSV upload & auto-clean",
      "Dashboard + AI summary",
      "PDF or Excel export",
    ],
    highlighted: false,
    cta: "Start a gig",
  },
  {
    name: "Growth",
    price: "$200 – $500",
    period: "/ month",
    description: "Recurring analytics for growing teams.",
    features: [
      "Monthly KPI reports & dashboards",
      "Domain-aware insights",
      "Priority email support",
      "Branded PDF + PPTX delivery",
    ],
    highlighted: true,
    cta: "Book a call",
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "one-time or retainer",
    description: "Full custom bot or dashboard build.",
    features: [
      "Custom Streamlit app development",
      "NL→SQL + RAG on your data",
      "Deployment & handoff docs",
      "Optional white-label branding",
    ],
    highlighted: false,
    cta: "Request quote",
  },
];

export const testimonials = [
  {
    quote: "Delivered a full client dashboard in under 48 hours — auto-clean, KPIs, and a PDF report the client loved.",
    author: "Fiverr client",
    role: "Excel automation project",
    metric: "48h delivery",
  },
  {
    quote: "The DataBot handles domain detection and SQL questions my team used to queue with an analyst for days.",
    author: "Analytics lead",
    role: "SaaS startup",
    metric: "10× faster Q&A",
  },
  {
    quote: "Cross-filter dashboards and executive view made our monthly board deck basically generate itself.",
    author: "Operations manager",
    role: "E-commerce brand",
    metric: "3 formats exported",
  },
];

export const techStack = [
  "Python", "Pandas", "Streamlit", "Plotly", "DuckDB", "FAISS",
  "Claude", "OpenAI", "ReportLab", "python-pptx",
];
