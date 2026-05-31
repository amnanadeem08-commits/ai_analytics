import { site } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import SectionHeader from "../ui/SectionHeader";

export default function Contact() {
  const mailto = `mailto:${site.email}?subject=AI%20services%20inquiry`;

  return (
    <AnimatedSection id="contact" className="bg-surface/50">
      <div className="overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-card via-surface to-accent/10 p-8 sm:p-12 lg:p-16">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div>
            <SectionHeader
              align="left"
              eyebrow="Contact"
              title="Let's build your next analytics win"
              subtitle="Available for Fiverr, Upwork, and direct projects. Typical response within 24 hours."
            />
            <div className="flex flex-wrap gap-3">
              <Button href={mailto} size="lg">
                Email {site.name}
              </Button>
              <Button href={site.github} variant="secondary" size="lg" external>
                GitHub →
              </Button>
            </div>
          </div>

          <form
            className="glass rounded-2xl p-6"
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.target);
              const subject = encodeURIComponent(String(fd.get("subject") || "Project inquiry"));
              const body = encodeURIComponent(
                `Name: ${fd.get("name")}\n\n${fd.get("message")}`,
              );
              window.location.href = `mailto:${site.email}?subject=${subject}&body=${body}`;
            }}
          >
            <label className="block text-sm font-medium text-muted">
              Name
              <input
                name="name"
                required
                className="mt-1.5 w-full rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none focus:border-accent"
                placeholder="Your name"
              />
            </label>
            <label className="mt-4 block text-sm font-medium text-muted">
              Subject
              <input
                name="subject"
                className="mt-1.5 w-full rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none focus:border-accent"
                placeholder="Dashboard build / Excel gig / Custom bot"
              />
            </label>
            <label className="mt-4 block text-sm font-medium text-muted">
              Message
              <textarea
                name="message"
                required
                rows={4}
                className="mt-1.5 w-full resize-none rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none focus:border-accent"
                placeholder="Tell me about your data, timeline, and budget..."
              />
            </label>
            <Button type="submit" className="mt-6 w-full">
              Send message
            </Button>
          </form>
        </div>
      </div>
    </AnimatedSection>
  );
}
