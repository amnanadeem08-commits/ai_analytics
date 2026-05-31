import { pricing } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import SectionHeader from "../ui/SectionHeader";

export default function Pricing() {
  return (
    <AnimatedSection id="pricing">
      <SectionHeader
        eyebrow="Pricing"
        title="Scoped To Your Project"
        subtitle="Every build is quoted after understanding your data, timeline, and deliverables — no fake price tags."
      />
      <div className="grid gap-4 lg:grid-cols-3 lg:gap-5">
        {pricing.map((plan) => (
          <article
            key={plan.name}
            className={`flex flex-col rounded-2xl border p-6 transition-all duration-300 sm:p-7 ${
              plan.highlighted
                ? "glass border-accent/40 bg-gradient-to-b from-accent/15 to-white/[0.03] shadow-glow lg:scale-[1.02]"
                : "glass-card border-white/10 hover:border-accent/25"
            }`}
          >
            {plan.highlighted && (
              <span className="mb-3 inline-block w-fit rounded-full bg-accent/20 px-3 py-1 text-xs font-bold text-accent-light">
                Most requested
              </span>
            )}
            <h3 className="text-lg font-bold text-white">{plan.name}</h3>
            <p className="mt-2 text-sm text-muted">{plan.description}</p>
            <p className="mt-5 font-mono text-2xl font-bold text-white sm:text-3xl">{plan.price}</p>
            <ul className="mt-6 flex-1 space-y-2.5 text-sm text-muted">
              {plan.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span className="text-mint" aria-hidden>
                    ✓
                  </span>
                  {f}
                </li>
              ))}
            </ul>
            <Button
              href="#contact"
              variant={plan.highlighted ? "primary" : "secondary"}
              className="mt-6 w-full"
              size="md"
            >
              {plan.cta}
            </Button>
          </article>
        ))}
      </div>
    </AnimatedSection>
  );
}
