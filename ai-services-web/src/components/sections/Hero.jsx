import { hero, site } from "../../data/content";
import Button from "../ui/Button";
import DashboardMockup from "../ui/DashboardMockup";

export default function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden pt-24 pb-12 sm:pt-28 sm:pb-16 lg:pt-32 lg:pb-20"
    >
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_20%_-5%,rgba(108,99,255,0.22),transparent)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-24 top-32 h-72 w-72 rounded-full bg-mint/10 blur-3xl"
        aria-hidden
      />

      <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-12">
          <div className="max-w-xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold text-accent-light">
              <span className="h-1.5 w-1.5 rounded-full bg-mint animate-pulse" />
              {hero.byline} · Available for hire
            </div>

            <h1 className="text-3xl font-black leading-tight tracking-tight sm:text-4xl lg:text-[2.75rem] lg:leading-[1.1]">
              {hero.headline}
            </h1>

            <p className="mt-2 text-sm font-medium text-white/90">
              Freelance service provider · Fiverr · Upwork · Direct clients
            </p>

            <p className="mt-4 text-base leading-relaxed text-muted sm:text-lg">
              {hero.subheadline}
            </p>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Button href={site.demos.dataBot} size="lg" external>
                See Live Demo
              </Button>
              <Button href="#contact" variant="secondary" size="lg">
                Hire Me
              </Button>
            </div>

            <ul className="mt-6 flex flex-wrap gap-2" aria-label="Technologies">
              {hero.trust.map((item) => (
                <li key={item} className="trust-pill">
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="relative lg:pl-4">
            <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-accent/20 via-transparent to-mint/10 blur-2xl" aria-hidden />
            <DashboardMockup className="relative animate-float" />
          </div>
        </div>
      </div>
    </section>
  );
}
