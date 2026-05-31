export default function Card({ children, className = "", hover = true, glass = true }) {
  const base = glass
    ? "glass-card p-5 sm:p-6"
    : "rounded-2xl border border-white/10 bg-card p-5 sm:p-6";

  return (
    <div
      className={`${base} ${
        hover && !glass
          ? "transition-all duration-300 hover:-translate-y-1 hover:border-accent/30 hover:shadow-glow"
          : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
