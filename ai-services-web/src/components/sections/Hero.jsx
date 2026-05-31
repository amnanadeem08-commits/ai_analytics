import { site } from "../../data/content";
import Button from "../ui/Button";

export default function Hero() {
  return (
    <section
      id="top"
      className="relative min-h-screen overflow-hidden pt-28 pb-16 sm:pt-32 lg:pt-36"
    >
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(108,99,255,0.25),transparent)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-32 top-40 h-96 w-96 rounded-full bg-mint/10 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -left-32 bottom-20 h-80 w-80 rounded-full bg-accent/15 blur-3xl animate-float"
        aria-hidden
      />

      <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-semibold text-accent-light">
            <span className="h-1.5 w-1.5 rounded-full bg-mint animate-pulse" />
            AI bots · Dashboards · Automation
          </div>

          <h1 className="text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl lg:leading-[1.08]">
            Turn raw data into{" "}
            <span className="gradient-text">decisions — automatically</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted">
            Premium AI analytics bots and custom dashboard services for Fiverr, Upwork,
            and growing teams. Ship client-ready insights in hours, not weeks.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button href={site.demos.dataBot} size="lg" external>
              View DataBot Live →
            </Button>
            <Button href="#contact" variant="secondary" size="lg">
              Hire {site.name}
            </Button>
          </div>

          <dl className="mt-16 grid grid-cols-3 gap-4 border-t border-white/10 pt-10 sm:gap-8">
            {[
              { label: "Domains", value: "10+" },
              { label: "Live demos", value: "2" },
              { label: "Export formats", value: "3" },
            ].map((stat) => (
              <div key={stat.label}>
                <dt className="text-xs uppercase tracking-wider text-muted">{stat.label}</dt>
                <dd className="mt-1 font-mono text-2xl font-bold text-white">{stat.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
