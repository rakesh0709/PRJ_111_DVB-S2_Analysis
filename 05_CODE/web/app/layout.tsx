import type { Metadata } from "next";
import { IBM_Plex_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const ibmPlexSans = IBM_Plex_Sans({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "PRJ_111 | DVB-S2 Receiver Output Stream Analyzer",
  description:
    "Engineering workstation and technical showcase for multi-format DVB-S2 receiver output streams (MPEG-TS, GSE, BBFrame). Features F1-F7 pipeline with AI anomaly detection.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${ibmPlexSans.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-[#0A0A0A] text-[#E8E8E8] antialiased selection:bg-[#FF6B35] selection:text-[#0A0A0A]">
        {children}
      </body>
    </html>
  );
}
