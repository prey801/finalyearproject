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
      <div className="flex-1 flex flex-col min-w-0 bg-[#FDFBF7]">
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
        {/* Persistent Clinical Safety Disclaimer */}
        <footer className="shrink-0 border-t-4 border-foreground bg-[#FDFBF7] py-2 px-4 flex justify-center items-center gap-2 text-xs text-foreground font-bold uppercase tracking-wider">
          <AlertCircle className="w-4 h-4 text-destructive" />
          <p>
            <strong>For research and secondary verification purposes only.</strong> Does not constitute a primary clinical diagnosis.
          </p>
        </footer>
      </div>
    </>
  );
}
