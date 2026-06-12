import React from "react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LegalX — AI Knowledge Centre for Indian Law",
  description:
    "AI-powered legal knowledge platform simplifying Indian law. Explore POCSO, Consumer Protection, Cyber Law, RTI, and GST with summaries, key insights, and interactive Q&A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="navbar">
          <div className="navbar-inner">
            <a href="/" className="navbar-brand">
              {/* SVG Shield + Scales Logo */}
              <span className="navbar-logo">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 32 32"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <defs>
                    <linearGradient id="logo-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stopColor="#818cf8" />
                      <stop offset="100%" stopColor="#c084fc" />
                    </linearGradient>
                  </defs>
                  {/* Shield outline */}
                  <path
                    d="M16 2L4 7v7c0 8.5 5.1 16.4 12 18 6.9-1.6 12-9.5 12-18V7L16 2z"
                    fill="url(#logo-grad)"
                    opacity="0.15"
                    stroke="url(#logo-grad)"
                    strokeWidth="1.5"
                  />
                  {/* Scales of justice */}
                  <line x1="16" y1="9" x2="16" y2="23" stroke="url(#logo-grad)" strokeWidth="1.8" strokeLinecap="round" />
                  <line x1="10" y1="12" x2="22" y2="12" stroke="url(#logo-grad)" strokeWidth="1.8" strokeLinecap="round" />
                  {/* Left pan */}
                  <path d="M10 12L8 17h4L10 12z" fill="url(#logo-grad)" opacity="0.6" />
                  {/* Right pan */}
                  <path d="M22 12L20 17h4L22 12z" fill="url(#logo-grad)" opacity="0.6" />
                  {/* Base */}
                  <line x1="12" y1="23" x2="20" y2="23" stroke="url(#logo-grad)" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </span>
              <span className="navbar-brand-text">
                <span className="brand-legal">Legal</span>
                <span className="brand-x">X</span>
              </span>
              <span className="navbar-badge">AI Powered</span>
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
