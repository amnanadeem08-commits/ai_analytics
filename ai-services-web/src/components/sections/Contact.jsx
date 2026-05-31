import { site } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";

export default function Contact() {
  const mailto = `mailto:${site.email}?subject=AI%20automation%20consultation`;

  return (
    <AnimatedSection id="contact" className="bg-surface/40">
      <div className="overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-card via-surface to-accent/10 p-6 sm:p-10 lg:p-12">
        <div className="grid gap-8 lg:grid-cols-2 lg:items-center lg:gap-10">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-accent-light">
              Get started
            </p>
            <h2 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl lg:text-4xl">
              Ready To Automate Your Workflow?
            </h2>
            <p className="mt-3 text-base leading-relaxed text-muted">
              Tell me about your reporting pain points, data sources, and timeline. I respond within
              24 hours for Fiverr, Upwork, and direct projects.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Button href={mailto} size="lg">
                Contact Me
              </Button>
              <Button href="#bots" variant="secondary" size="lg">
                View Projects
              </Button>
              <Button
                href={`mailto:${site.email}?subject=Book%20consultation%20-%20AI%20automation`}
                variant="secondary"
                size="lg"
              >
                Book Consultation
              </Button>
            </div>
          </div>

          <form
            className="glass rounded-2xl p-5 sm:p-6"
            aria-label="Contact form"
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
                autoComplete="name"
                className="mt-1.5 w-full rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none transition-colors focus:border-accent"
                placeholder="Your name"
              />
            </label>
            <label className="mt-4 block text-sm font-medium text-muted">
              Subject
              <input
                name="subject"
                className="mt-1.5 w-full rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none transition-colors focus:border-accent"
                placeholder="Automation / Dashboard / Custom AI bot"
              />
            </label>
            <label className="mt-4 block text-sm font-medium text-muted">
              Message
              <textarea
                name="message"
                required
                rows={4}
                className="mt-1.5 w-full resize-none rounded-xl border border-white/10 bg-canvas px-4 py-2.5 text-white outline-none transition-colors focus:border-accent"
                placeholder="Describe your workflow, files, and deadline..."
              />
            </label>
            <Button type="submit" className="mt-5 w-full" size="md">
              Send message
            </Button>
          </form>
        </div>
      </div>
    </AnimatedSection>
  );
}
