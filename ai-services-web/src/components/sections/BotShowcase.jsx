import { bots } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import DashboardMockup from "../ui/DashboardMockup";
import SectionHeader from "../ui/SectionHeader";
import WorkflowViz from "../ui/WorkflowViz";

export default function BotShowcase() {
  return (
    <AnimatedSection id="bots" className="bg-surface/40">
      <SectionHeader
        eyebrow="Live products"
        title="AI Systems In Action"
        subtitle="Production bots you can demo today — each solves a specific reporting or automation problem."
      />

      <div className="space-y-8">
        {bots.map((bot, index) => (
          <article
            key={bot.name}
            className={`glass overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br ${bot.gradient}`}
          >
            <div
              className={`grid gap-6 p-6 sm:p-8 lg:grid-cols-2 lg:items-center ${
                index % 2 === 1 ? "lg:[direction:rtl]" : ""
              }`}
            >
              <div className={index % 2 === 1 ? "lg:[direction:ltr]" : ""}>
                <DashboardMockup variant={bot.variant} />
              </div>

              <div className={index % 2 === 1 ? "lg:[direction:ltr]" : ""}>
                <p className="text-xs font-bold uppercase tracking-widest text-accent-light">
                  {bot.role}
                </p>
                <h3 className="mt-2 text-xl font-bold text-white sm:text-2xl">{bot.name}</h3>
                <p className="mt-3 text-sm leading-relaxed text-white/85">
                  <span className="font-semibold text-mint">Problem solved: </span>
                  {bot.problem}
                </p>
                <ul className="mt-4 space-y-2">
                  {bot.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-white/90">
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-mint/20 text-xs text-mint">
                        ✓
                      </span>
                      {f}
                    </li>
                  ))}
                </ul>
                <div className="mt-4 flex flex-wrap gap-2">
                  {bot.stack.map((t) => (
                    <span
                      key={t}
                      className="rounded-md border border-white/15 bg-black/25 px-2.5 py-1 text-xs font-medium text-muted"
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <div className="mt-6 flex flex-wrap gap-3">
                  <Button href={bot.demo} external size="md">
                    Live demo
                  </Button>
                  <Button href={bot.github} variant="secondary" size="md" external>
                    GitHub
                  </Button>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="mt-10">
        <WorkflowViz />
      </div>
    </AnimatedSection>
  );
}
