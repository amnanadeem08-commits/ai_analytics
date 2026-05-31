export const site = {
  name: "Amna Malik",
  brand: "DataBot AI",
  title: "Data & AI Engineer",
  email: "amnamalikk.007l@gmail.com",
  github: "https://github.com/amnanadeem08-commits",
  repo: "https://github.com/amnanadeem08-commits/ai_analytics",
  website: "https://amnanadeem08-commits.github.io/ai_analytics/",
  demos: {
    dataBot: "https://data-analytics-bot.streamlit.app/",
    excelBot: "https://excelmvp-muqntkjoq8527pxpxevcuj.streamlit.app/",
  },
};

export const navLinks = [
  { href: "#services", label: "Services" },
  { href: "#bots", label: "Solutions" },
  { href: "#proof", label: "Why Me" },
  { href: "#process", label: "Process" },
  { href: "#pricing", label: "Pricing" },
  { href: "#contact", label: "Contact" },
];

export const hero = {
  byline: "Amna Malik · Data & AI Engineer",
  headline: "AI Automation & Analytics Solutions",
  subheadline:
    "I build custom AI bots, dashboards, and reporting systems for businesses and freelancers — so you spend less time on manual work and get insights faster.",
  trust: ["Python", "SQL", "Power BI", "AI", "Automation"],
};

export const painPoints = [
  {
    icon: "📊",
    title: "Manual Excel work consuming time",
    body: "Hours spent cleaning sheets, fixing formulas, and rebuilding the same reports every week.",
  },
  {
    icon: "🔁",
    title: "Repetitive reporting tasks",
    body: "Monthly decks and KPI packs that should run themselves still depend on manual copy-paste.",
  },
  {
    icon: "🐢",
    title: "Slow business insights",
    body: "Questions sit in queue while teams wait for an analyst to pull numbers and explain them.",
  },
  {
    icon: "🖥️",
    title: "Dashboard maintenance headaches",
    body: "Broken filters, stale data sources, and one-off fixes that never scale across the business.",
  },
  {
    icon: "🧹",
    title: "File cleaning frustration",
    body: "Messy CSV and Excel uploads that need normalization before anyone can trust the charts.",
  },
];

export const painClosing = "I build systems that automate this.";

export const services = [
  {
    icon: "🤖",
    title: "AI Analytics Bot",
    tagline: "Upload data → AI analyzes → Reports generated automatically",
    bullets: ["CSV / Excel uploads", "Automated insights", "Report exports"],
    cta: "See live demo",
    href: site.demos.dataBot,
  },
  {
    icon: "📈",
    title: "Dashboard Development",
    tagline: "Executive-ready KPI monitoring and interactive views",
    bullets: ["Power BI", "Tableau", "Excel dashboards", "KPI monitoring"],
    cta: "Discuss project",
    href: "#contact",
  },
  {
    icon: "⚙️",
    title: "Automation Systems",
    tagline: "Pipelines and workflows that run without manual touch",
    bullets: ["Reporting automation", "Workflow automation", "Data pipelines"],
    cta: "Get custom quote",
    href: "#contact",
  },
  {
    icon: "✨",
    title: "Custom AI Solutions",
    tagline: "Tailored assistants and internal tools for your team",
    bullets: ["Chatbots", "Analytics assistants", "Internal tools"],
    cta: "Book consultation",
    href: "#contact",
  },
];

export const bots = [
  {
    name: "AI Data Reporting & Analytics Assistant",
    role: "Full analytics platform",
    problem: "Replaces manual reporting, SQL queries, and slide-deck assembly with one upload workflow.",
    features: ["Smart domain detection", "Cross-filter dashboards", "Branded PDF/PPTX/Excel exports"],
    stack: ["Streamlit", "DuckDB", "FAISS", "Plotly", "Claude"],
    demo: site.demos.dataBot,
    github: site.repo,
    variant: "analytics",
    gradient: "from-accent/30 to-violet-500/20",
  },
  {
    name: "Excel Automation AI Tool",
    role: "Spreadsheet automation product",
    problem: "Turns messy Excel/CSV uploads into cleaned data, charts, and client-ready reports in minutes.",
    features: ["One-click clean & chart", "AI executive summary", "Multi-format export"],
    stack: ["Python", "Pandas", "ReportLab", "python-pptx", "Plotly"],
    demo: site.demos.excelBot,
    github: site.repo,
    variant: "excel",
    gradient: "from-mint/20 to-accent/20",
  },
];

export const trustPoints = [
  {
    icon: "🚀",
    title: "Production-focused builds",
    body: "Shippable systems with real upload flows, exports, and hosting — not mockups.",
  },
  {
    icon: "📄",
    title: "Documentation included",
    body: "Clear handoff notes so your team knows how to run, update, and extend the solution.",
  },
  {
    icon: "🎯",
    title: "Custom solutions",
    body: "Scope aligned to your data, KPIs, and delivery format — not one-size-fits-all templates.",
  },
  {
    icon: "📤",
    title: "Export support",
    body: "PDF, PowerPoint, Excel, and dashboard outputs ready for clients and stakeholders.",
  },
  {
    icon: "🧠",
    title: "AI + Analytics expertise",
    body: "Python, SQL, BI tools, and LLM integrations combined into practical automation.",
  },
];

export const trustCounters = [
  { label: "Projects", value: 2, suffix: "+" },
  { label: "Tools", value: 10, suffix: "+" },
  { label: "Exports", value: 3, suffix: "" },
  { label: "Automations", value: 8, suffix: "+" },
];

export const processSteps = [
  {
    step: "1",
    title: "Requirements",
    body: "Goals, data sources, KPIs, timeline, and delivery format captured up front.",
  },
  {
    step: "2",
    title: "Build",
    body: "Bot, dashboard, or pipeline developed with iterative check-ins.",
  },
  {
    step: "3",
    title: "Testing",
    body: "Real files, edge cases, and export quality validated before handoff.",
  },
  {
    step: "4",
    title: "Delivery",
    body: "Hosted demo, source access, and documentation delivered together.",
  },
  {
    step: "5",
    title: "Support",
    body: "Post-launch fixes and enhancement options based on your scope.",
  },
];

export const pricing = [
  {
    name: "Starter",
    price: "Custom Quote",
    period: "",
    description: "Simple automation — Excel/CSV workflows, single reports, or quick bot setups.",
    features: [
      "Scoped automation or report build",
      "Clear delivery timeline",
      "Export-ready output",
    ],
    highlighted: false,
    cta: "Request quote",
  },
  {
    name: "Professional",
    price: "Custom Quote",
    period: "",
    description: "Dashboards plus AI workflows — recurring reporting and interactive analytics.",
    features: [
      "Dashboard + AI assistant combo",
      "KPI design & automation",
      "Documentation & handoff",
    ],
    highlighted: true,
    cta: "Request quote",
  },
  {
    name: "Custom",
    price: "Custom Quote",
    period: "",
    description: "Complex systems — multi-step pipelines, custom copilots, and internal tools.",
    features: [
      "Full custom architecture",
      "Integrations & hosting guidance",
      "Ongoing support options",
    ],
    highlighted: false,
    cta: "Book consultation",
  },
];

export const techStack = [
  "Python", "SQL", "Pandas", "Streamlit", "Plotly", "Power BI", "Tableau",
  "DuckDB", "FAISS", "Claude", "OpenAI", "ReportLab", "python-pptx",
];
