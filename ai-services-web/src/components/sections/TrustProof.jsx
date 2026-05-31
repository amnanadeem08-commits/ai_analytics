import { trustCounters, trustPoints } from "../../data/content";
import { useInView } from "../../hooks/useInView";
import { useCountUp } from "../../hooks/useCountUp";
import AnimatedSection from "../ui/AnimatedSection";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

function Counter({ label, value, suffix, active }) {
  const count = useCountUp(value, active);

  return (
    <div className="text-center">
      <p className="font-mono text-3xl font-bold text-white sm:text-4xl">
        {count}
        {suffix}
      </p>
      <p className="mt-1 text-xs font-semibold uppercase tracking-wider text-muted">{label}</p>
    </div>
  );
}

export default function TrustProof() {
  const { ref, visible } = useInView(0.2);

  return (
    <AnimatedSection id="proof">
      <SectionHeader
        eyebrow="Trust"
        title="Why Work With Me"
        subtitle="Focused on delivery, documentation, and systems your clients can actually use."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {trustPoints.map((item) => (
          <Card key={item.title}>
            <span className="text-2xl" aria-hidden>
              {item.icon}
            </span>
            <h3 className="mt-3 text-base font-bold text-white">{item.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{item.body}</p>
          </Card>
        ))}
      </div>

      <div
        ref={ref}
        className="glass mt-8 grid grid-cols-2 gap-6 rounded-2xl border border-white/10 p-6 sm:grid-cols-4 sm:p-8"
      >
        {trustCounters.map((c) => (
          <Counter
            key={c.label}
            label={c.label}
            value={c.value}
            suffix={c.suffix}
            active={visible}
          />
        ))}
      </div>
    </AnimatedSection>
  );
}
