const steps = ["Upload Data", "AI Analysis", "Dashboard Creation", "Export Results"];

export default function WorkflowViz() {
  return (
    <div className="glass rounded-2xl border border-white/10 p-6 sm:p-8">
      <p className="mb-6 text-center text-sm font-semibold uppercase tracking-widest text-accent-light">
        End-to-end workflow
      </p>
      <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-2">
        {steps.map((step, i) => (
          <div key={step} className="flex flex-col items-center sm:flex-1 sm:flex-row">
            <div className="flex w-full flex-col items-center rounded-xl border border-white/10 bg-white/[0.03] px-3 py-4 text-center transition-colors hover:border-accent/30 sm:flex-1">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/20 text-sm font-bold text-accent-light">
                {i + 1}
              </span>
              <span className="mt-2 text-xs font-semibold text-white sm:text-sm">{step}</span>
            </div>
            {i < steps.length - 1 && (
              <span className="py-1 text-center text-lg text-accent/60 sm:px-2 sm:py-0" aria-hidden>
                ↓
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
