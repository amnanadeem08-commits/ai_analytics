const variants = {
  primary:
    "bg-gradient-to-r from-accent to-violet-600 text-white shadow-glow hover:shadow-glow-lg hover:brightness-110",
  secondary:
    "glass text-white hover:border-accent/50 hover:bg-white/[0.06]",
  ghost: "text-muted hover:text-white hover:bg-white/5",
};

const sizes = {
  sm: "px-4 py-2.5 text-sm min-h-[40px]",
  md: "px-5 py-3 text-sm min-h-[44px]",
  lg: "px-7 py-3.5 text-base min-h-[48px]",
};

export default function Button({
  children,
  href,
  variant = "primary",
  size = "md",
  className = "",
  external = false,
  ...props
}) {
  const classes = `inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-canvas ${variants[variant]} ${sizes[size]} ${className}`;

  if (href) {
    return (
      <a
        href={href}
        className={classes}
        {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
      >
        {children}
      </a>
    );
  }

  return (
    <button type="button" className={classes} {...props}>
      {children}
    </button>
  );
}
