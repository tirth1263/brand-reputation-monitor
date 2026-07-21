import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Brand Reputation Monitor",
  description:
    "Evidence-first brand intelligence powered by live news, Bright Data, and Nebius AI.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

