import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "0Gora",
  description: "The community-crowdsourced knowledge commons — verifiable AI answers on 0G.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
