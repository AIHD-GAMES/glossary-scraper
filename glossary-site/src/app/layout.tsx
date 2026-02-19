import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "投資部 用語集 | 資産運用のための専門用語解説",
  description: "投資初心者から上級者まで、5,000語以上の金融・証券用語を分かりやすく解説。検索機能や五十音順インデックスで必要な情報をすぐに見つけられます。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="scroll-smooth">
      <body className={`${inter.variable} ${outfit.variable} font-sans antialiased text-slate-900`}>
        {children}
      </body>
    </html>
  );
}
