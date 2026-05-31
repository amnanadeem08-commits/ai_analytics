export default function SectionHeader({ eyebrow, title, subtitle, align = "center" }) {
  const alignClass = align === "center" ? "text-center mx-auto" : "text-left";

  return (
    <header className={`mb-12 max-w-2xl ${alignClass}`}>
      {eyebrow && (
        <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-accent-light">
          {eyebrow}
        </p>
      )}
      <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl lg:text-[2.5rem]">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-base leading-relaxed text-muted sm:text-lg">{subtitle}</p>
      )}
    </header>
  );
}
