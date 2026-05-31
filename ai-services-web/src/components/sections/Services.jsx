import { services } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

export default function Services() {
  return (
    <AnimatedSection id="services">
      <SectionHeader
        eyebrow="Services"
        title="Everything you need to deliver analytics"
        subtitle="From one-off Excel gigs to full AI platforms — pick the layer that fits your client."
      />
      <div className="grid gap-6 md:grid-cols-2">
        {services.map((svc) => (
          <Card key={svc.title} className="flex flex-col">
            <div className="flex items-start gap-4">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent/15 text-2xl">
                {svc.icon}
              </span>
              <div>
                <h3 className="text-xl font-bold text-white">{svc.title}</h3>
                <p className="text-sm font-medium text-accent-light">{svc.tagline}</p>
              </div>
            </div>
            <ul className="mt-5 flex-1 space-y-2 text-sm text-muted">
              {svc.bullets.map((b) => (
                <li key={b} className="flex gap-2">
                  <span className="text-accent">✦</span>
                  {b}
                </li>
              ))}
            </ul>
            <div className="mt-6">
              <Button
                href={svc.href}
                variant="secondary"
                size="sm"
                external={svc.href.startsWith("http")}
              >
                {svc.cta} →
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </AnimatedSection>
  );
}
