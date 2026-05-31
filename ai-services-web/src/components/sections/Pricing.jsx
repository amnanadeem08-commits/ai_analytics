import { pricing } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import SectionHeader from "../ui/SectionHeader";

export default function Pricing() {
  return (
    <AnimatedSection id="pricing" className="bg-surface/50">
      <SectionHeader
        eyebrow="Pricing"
        title="Simple, transparent packages"
        subtitle="From quick Excel gigs to monthly retainers and full custom builds."
      />
      <div className="grid gap-6 lg:grid-cols-3">
        {pricing.map((plan) => (
          <article
            key={plan.name}
            className={`flex flex-col rounded-2xl border p-8 transition-all duration-300 ${
              plan.highlighted
                ? "border-accent/50 bg-gradient-to-b from-accent/15 to-card shadow-glow scale-[1.02]"
                : "border-white/10 bg-card hover:border-accent/30"
            }`}
          >
            {plan.highlighted && (
              <span className="mb-4 inline-block w-fit rounded-full bg-accent/20 px-3 py-1 text-xs font-bold text-accent-light">
                Most popular
              </span>
            )}
            <h3 className="text-lg font-bold text-white">{plan.name}</h3>
            <p className="mt-2 text-sm text-muted">{plan.description}</p>
            <p className="mt-6 font-mono text-3xl font-bold text-white">
              {plan.price}
              <span className="ml-1 text-sm font-normal text-muted">{plan.period}</span>
            </p>
            <ul className="mt-8 flex-1 space-y-3 text-sm text-muted">
              {plan.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span className="text-mint">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <Button
              href="#contact"
              variant={plan.highlighted ? "primary" : "secondary"}
              className="mt-8 w-full"
            >
              {plan.cta}
            </Button>
          </article>
        ))}
      </div>
    </AnimatedSection>
  );
}
