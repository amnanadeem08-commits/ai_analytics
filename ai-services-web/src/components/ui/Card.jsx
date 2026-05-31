export default function Card({ children, className = "", hover = true }) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-card p-6 ${
        hover ? "transition-all duration-300 hover:-translate-y-1 hover:border-accent/30 hover:shadow-glow" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
