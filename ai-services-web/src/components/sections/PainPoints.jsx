import { painPoints } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

export default function PainPoints() {
  return (
    <AnimatedSection className="bg-surface/50">
      <SectionHeader
        eyebrow="The problem"
        title="Analytics shouldn't be this hard"
        subtitle="Most teams are stuck in manual workflows that slow every decision."
      />
      <div className="grid gap-5 sm:grid-cols-2">
        {painPoints.map((item) => (
          <Card key={item.title}>
            <span className="text-2xl" aria-hidden>
              {item.icon}
            </span>
            <h3 className="mt-4 text-lg font-bold text-white">{item.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{item.body}</p>
          </Card>
        ))}
      </div>
    </AnimatedSection>
  );
}
