import { Sidebar } from "@/components/layout/Sidebar";
import { AlertCircle } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
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
    </>
  );
}
