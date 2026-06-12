import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LegalX — AI Knowledge Centre for Indian Law",
  description:
    "AI-powered legal knowledge platform simplifying Indian law. Explore POCSO, Consumer Protection, Cyber Law, RTI, and GST with summaries, key insights, and interactive Q&A.",
  keywords: ["Indian law", "legal AI", "POCSO", "Consumer Protection", "RTI", "GST", "Cyber Law"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="navbar">
          <div className="navbar-inner">
            <a href="/" className="navbar-brand">
              <span className="navbar-brand-icon">⚖️</span>
              LegalX
              <span className="navbar-badge">AI</span>
            </a>
          </div>
        </nav>
        <main>{children}</main>
        <footer className="footer">
          <p>LegalX AI Knowledge Centre · Built for simplifying Indian law</p>
        </footer>
      </body>
    </html>
  );
}
