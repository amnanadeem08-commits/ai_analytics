/** CSS-only dashboard preview for hero & bot showcase — no external images. */
export default function DashboardMockup({ variant = "analytics", className = "" }) {
  const accent = variant === "excel" ? "from-mint/40 to-emerald-600/30" : "from-accent/40 to-violet-600/30";

  return (
    <div
      className={`glass relative overflow-hidden rounded-2xl border border-white/15 shadow-glow-lg ${className}`}
      aria-hidden
    >
      <div className="flex items-center gap-2 border-b border-white/10 bg-black/20 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
        <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/80" />
        <span className="h-2.5 w-2.5 rounded-full bg-mint/80" />
        <span className="ml-2 text-xs font-medium text-muted">
          {variant === "excel" ? "Excel Automation Bot" : "AI Analytics Dashboard"}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 p-3 sm:gap-3 sm:p-4">
        {[
          { label: "Records", value: "12.4K", delta: "+18%" },
          { label: "Insights", value: "47", delta: "AI" },
          { label: "Exports", value: "3", delta: "PDF" },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-xl border border-white/10 bg-white/[0.03] p-2 sm:p-3"
          >
            <p className="text-[10px] uppercase tracking-wider text-muted sm:text-xs">{kpi.label}</p>
            <p className="font-mono text-sm font-bold text-white sm:text-lg">{kpi.value}</p>
            <p className="text-[10px] text-mint sm:text-xs">{kpi.delta}</p>
          </div>
        ))}
      </div>

      <div className="px-3 pb-3 sm:px-4 sm:pb-4">
        <div className={`rounded-xl bg-gradient-to-br ${accent} p-3 sm:p-4`}>
          <div className="mb-3 flex items-end justify-between gap-1 sm:gap-1.5" style={{ height: 88 }}>
            {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t bg-white/25 animate-pulse"
                style={{
                  height: `${h}%`,
                  animationDelay: `${i * 0.08}s`,
                  animationDuration: "2.4s",
                }}
              />
            ))}
          </div>
          <div className="flex items-center justify-between text-[10px] text-white/70 sm:text-xs">
            <span>Auto-generated charts</span>
            <span className="rounded-full bg-mint/20 px-2 py-0.5 text-mint">Live</span>
          </div>
        </div>

        <div className="mt-2 flex gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
            <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-accent to-mint animate-shimmer bg-[length:200%_100%]" />
          </div>
          <span className="text-[10px] text-muted">Processing…</span>
        </div>
      </div>
    </div>
  );
}
