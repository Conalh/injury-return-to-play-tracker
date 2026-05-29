import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Return-to-play tracker",
  description: "Clinician dashboard for staged return-to-play evidence.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
