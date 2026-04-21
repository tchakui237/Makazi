import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Makazi — Analyse Immobiliere Yaounde",
  description:
    "Plateforme d'analyse immobiliere intelligente pour le marche locatif de Yaounde. Collecte de donnees et prediction de loyers par regression OLS.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.className} bg-[#0f172a] text-slate-50 antialiased`}>
        {children}
      </body>
    </html>
  );
}
