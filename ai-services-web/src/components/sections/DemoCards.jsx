import { demos } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

export default function DemoCards() {
  return (
    <AnimatedSection id="demos">
      <SectionHeader
        eyebrow="Live demos"
        title="See it in action"
        subtitle="Click through real deployments — no mockups, no screenshots-only promises."
      />
      <div className="grid gap-6 md:grid-cols-2">
        {demos.map((demo) => (
          <Card key={demo.title} className="group relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            <div className="relative">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/15 text-3xl">
                {demo.image}
              </div>
              <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-mint">
                {demo.stats}
              </p>
              <h3 className="mt-2 text-xl font-bold text-white">{demo.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{demo.description}</p>
              <div className="mt-6">
                <Button href={demo.href} external variant="primary" size="sm">
                  Open live app ↗
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </AnimatedSection>
  );
}
