import { site, techStack } from "../../data/content";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-white/10 bg-surface/80 py-12">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-lg font-bold text-white">{site.brand}</p>
            <p className="mt-1 text-sm text-muted">{site.name} · {site.title}</p>
            <p className="mt-4 max-w-sm text-sm text-muted">
              AI bots, dashboards, and automation for freelancers and data-driven teams.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {techStack.slice(0, 6).map((t) => (
              <span
                key={t}
                className="rounded-md border border-white/10 bg-card px-2 py-1 text-xs text-muted"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
        <p className="mt-10 border-t border-white/10 pt-6 text-center text-xs text-muted">
          © {year} {site.name}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
