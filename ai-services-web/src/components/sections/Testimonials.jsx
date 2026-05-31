import { testimonials } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

export default function Testimonials() {
  return (
    <AnimatedSection id="proof">
      <SectionHeader
        eyebrow="Proof"
        title="Trusted by clients & teams"
        subtitle="Real outcomes from analytics automation and AI bot deployments."
      />
      <div className="grid gap-6 md:grid-cols-3">
        {testimonials.map((t) => (
          <Card key={t.author + t.metric} hover={false} className="flex flex-col">
            <p className="flex-1 text-sm leading-relaxed text-white/90">&ldquo;{t.quote}&rdquo;</p>
            <div className="mt-6 border-t border-white/10 pt-4">
              <p className="font-semibold text-white">{t.author}</p>
              <p className="text-xs text-muted">{t.role}</p>
              <p className="mt-3 inline-block rounded-md bg-accent/15 px-2 py-1 font-mono text-xs font-bold text-accent-light">
                {t.metric}
              </p>
            </div>
          </Card>
        ))}
      </div>
    </AnimatedSection>
  );
}
