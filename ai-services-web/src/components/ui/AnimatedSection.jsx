import { useInView } from "../../hooks/useInView";

export default function AnimatedSection({ children, className = "", id }) {
  const { ref, visible } = useInView();

  return (
    <section
      id={id}
      ref={ref}
      className={`section-pad transition-all duration-700 ${
        visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      } ${className}`}
    >
      <div className="mx-auto max-w-6xl">{children}</div>
    </section>
  );
}
