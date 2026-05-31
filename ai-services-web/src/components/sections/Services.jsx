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
        title="Solutions That Replace Manual Work"
        subtitle="Productized AI and analytics services — scoped for freelancers, teams, and growing businesses."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:gap-5">
        {services.map((svc) => (
          <Card key={svc.title} className="flex flex-col">
            <div className="flex items-start gap-3">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent/15 text-xl">
                {svc.icon}
              </span>
              <div>
                <h3 className="text-lg font-bold text-white sm:text-xl">{svc.title}</h3>
                <p className="mt-1 text-sm font-medium text-accent-light">{svc.tagline}</p>
              </div>
            </div>
            <ul className="mt-4 flex-1 space-y-2 text-sm text-muted">
              {svc.bullets.map((b) => (
                <li key={b} className="flex gap-2">
                  <span className="text-mint" aria-hidden>
                    ✓
                  </span>
                  {b}
                </li>
              ))}
            </ul>
            <div className="mt-5">
              <Button
                href={svc.href}
                variant="secondary"
                size="md"
                external={svc.href.startsWith("http")}
              >
                {svc.cta}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </AnimatedSection>
  );
}
