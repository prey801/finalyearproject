import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { AlertCircle } from "lucide-react";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MedScope AI",
  description: "AI-powered digital microscopy analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex h-screen overflow-hidden">
        <QueryProvider>
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 bg-background">
            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
            {/* Persistent Clinical Safety Disclaimer */}
            <footer className="shrink-0 border-t border-border bg-card/50 py-2 px-4 flex justify-center items-center gap-2 text-xs text-muted-foreground">
              <AlertCircle className="w-3.5 h-3.5" />
              <p>
                <strong>For research and secondary verification purposes only.</strong> Does not constitute a primary clinical diagnosis.
              </p>
            </footer>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
