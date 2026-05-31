import { bots } from "../../data/content";
import AnimatedSection from "../ui/AnimatedSection";
import Button from "../ui/Button";
import SectionHeader from "../ui/SectionHeader";

export default function BotShowcase() {
  return (
    <AnimatedSection id="bots" className="bg-surface/50">
      <SectionHeader
        eyebrow="Bot showcase"
        title="Production-ready AI bots"
        subtitle="Live Streamlit apps you can demo to clients today — or white-label for your gigs."
      />
      <div className="grid gap-8 lg:grid-cols-2">
        {bots.map((bot) => (
          <article
            key={bot.name}
            className={`relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br ${bot.gradient} p-8`}
          >
            <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/5 blur-2xl" />
            <div className="relative">
              <p className="text-xs font-bold uppercase tracking-widest text-accent-light">
                {bot.role}
              </p>
              <h3 className="mt-2 text-2xl font-bold text-white">{bot.name}</h3>
              <ul className="mt-6 space-y-2">
                {bot.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-white/90">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-mint/20 text-xs text-mint">
                      ✓
                    </span>
                    {f}
                  </li>
                ))}
              </ul>
              <div className="mt-6 flex flex-wrap gap-2">
                {bot.stack.map((t) => (
                  <span
                    key={t}
                    className="rounded-md border border-white/15 bg-black/20 px-2.5 py-1 text-xs font-medium text-muted"
                  >
                    {t}
                  </span>
                ))}
              </div>
              <div className="mt-8">
                <Button href={bot.demo} external size="md">
                  Launch demo →
                </Button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </AnimatedSection>
  );
}
