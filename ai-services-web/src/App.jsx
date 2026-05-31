import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Hero from "./components/sections/Hero";
import PainPoints from "./components/sections/PainPoints";
import Services from "./components/sections/Services";
import BotShowcase from "./components/sections/BotShowcase";
import DemoCards from "./components/sections/DemoCards";
import Pricing from "./components/sections/Pricing";
import Testimonials from "./components/sections/Testimonials";
import Contact from "./components/sections/Contact";

export default function App() {
  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2"
      >
        Skip to content
      </a>
      <Navbar />
      <main id="main">
        <Hero />
        <PainPoints />
        <Services />
        <BotShowcase />
        <DemoCards />
        <Pricing />
        <Testimonials />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
