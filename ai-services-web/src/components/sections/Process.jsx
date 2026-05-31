import { processSteps } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import SectionHeader from "../ui/SectionHeader";

export default function Process() {
  return (
    <AnimatedSection id="process" className="bg-surface/40">
      <SectionHeader
        eyebrow="Process"
        title="How Projects Work"
        subtitle="A clear path from requirements to delivery — with testing and support built in."
      />

      <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5 lg:gap-3">
        {processSteps.map((step, i) => (
          <li key={step.title} className="relative flex flex-col">
            <article className="glass-card flex h-full flex-col p-5">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-violet-600 text-sm font-bold text-white shadow-glow">
                {step.step}
              </span>
              <h3 className="mt-4 text-base font-bold text-white">{step.title}</h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-muted">{step.body}</p>
            </article>
            {i < processSteps.length - 1 && (
              <span
                className="pointer-events-none absolute -right-2 top-1/2 hidden -translate-y-1/2 text-accent/50 lg:inline"
                aria-hidden
              >
                →
              </span>
            )}
          </li>
        ))}
      </ol>
    </AnimatedSection>
  );
}
