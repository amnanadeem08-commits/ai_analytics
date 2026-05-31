import { painClosing, painPoints } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

export default function PainPoints() {
  return (
    <AnimatedSection className="bg-surface/40">
      <SectionHeader
        eyebrow="The problem"
        title="Still Spending Hours On Manual Reporting?"
        subtitle="Most teams lose time on work that should be automated — before insights ever reach decision-makers."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {painPoints.map((item) => (
          <Card key={item.title}>
            <span className="text-2xl" aria-hidden>
              {item.icon}
            </span>
            <h3 className="mt-3 text-base font-bold text-white sm:text-lg">{item.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{item.body}</p>
          </Card>
        ))}
      </div>
      <p className="mt-8 text-center text-lg font-semibold text-white sm:text-xl">
        <span className="gradient-text">{painClosing}</span>
      </p>
    </AnimatedSection>
  );
}
