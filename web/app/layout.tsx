import "./globals.css";
import type { Metadata } from "next";

const TITLE = "0Gora — the public square of verifiable knowledge on 0G";
const DESC =
  "0G + agora: a community-crowdsourced commons of verifiable knowledge. Create any town square — for anything, for anyone, human or agent. Every answer sealed in a 0G TEE.";

export const metadata: Metadata = {
  metadataBase: new URL("https://0gora.temporalabs.com"),
  title: TITLE,
  description: DESC,
  openGraph: {
    title: TITLE,
    description: DESC,
    url: "https://0gora.temporalabs.com",
    siteName: "0Gora",
    images: [{ url: "/cover.jpg", width: 1600, height: 900 }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESC,
    images: ["/cover.jpg"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
