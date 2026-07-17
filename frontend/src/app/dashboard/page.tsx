'use client';

import Link from 'next/link';
import { Activity, ImageIcon, CheckCircle, Clock, Search, Filter, MoreVertical, FileText, ChevronRight, AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { CaseSummaryPanel, CaseData } from '@/components/shared/CaseSummaryPanel';
import { getAnalysisHistory } from '@/lib/api';



export default function Home() {
  const [timeFilter, setTimeFilter] = useState('today');
  const [selectedCase, setSelectedCase] = useState<CaseData | null>(null);
  const [recentActivity, setRecentActivity] = useState<CaseData[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalysisHistory(0, 4)
      .then(data => {
        if (data && data.length > 0) {
          setRecentActivity(data.map(item => ({
            id: item.sample_id,
            date: 'Recent',
            patient: item.patient_id,
            type: item.specimen_type,
            status: item.review_required ? 'Review Required' : 'Completed',
            findings: item.prediction === 'malaria' ? `Abnormal (${item.parasitemia}%)` : 'Normal'
          })));
        }
        setError(null);
      })
      .catch(err => {
        console.error("Failed to fetch history from backend:", err);
        if (err.response?.status === 401) {
           setError("Authentication required. Please log in.");
        } else {
           setError("Failed to connect to the backend. Please ensure the server is running.");
        }
      });
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 relative">
      {/* Header section */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Workspace</h1>
          <p className="text-muted-foreground mt-1">Overview of your recent digital microscopy analyses</p>
        </div>
        <Link 
          href="/analyze" 
          className="bg-[#06b6d4] text-white border-2 border-foreground px-6 py-2.5 font-bold uppercase shadow-[4px_4px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-none transition-all flex items-center gap-2"
        >
          <Activity className="w-5 h-5" />
          New Analysis
        </Link>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}
      
      {/* KPI Grid with Time Filter */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold tracking-tight">Key Metrics</h2>
          <div className="flex bg-white border-2 border-foreground p-1 shadow-[4px_4px_0px_theme(colors.foreground)]">
            {['today', 'week', 'month', 'all'].map(filter => (
              <button
                key={filter}
                onClick={() => setTimeFilter(filter)}
                className={`px-4 py-1 text-sm font-bold uppercase border-2 transition-all ${
                  timeFilter === filter 
                    ? 'bg-foreground text-background border-foreground shadow-[2px_2px_0px_theme(colors.foreground)]' 
                    : 'bg-transparent border-transparent text-muted-foreground hover:border-foreground hover:text-foreground'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in-up stagger-1">
          <div className="bg-white border-4 border-foreground p-6 shadow-[6px_6px_0px_theme(colors.foreground)] flex flex-col gap-3 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 text-foreground">
              <ImageIcon className="w-5 h-5" />
              <span className="text-sm font-black uppercase tracking-wider">Images Analyzed</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-black tracking-tight text-foreground">142</span>
              <span className="text-xs text-green-600 font-bold uppercase border border-green-600 px-1 bg-green-50">+12% vs last {timeFilter}</span>
            </div>
          </div>
          
          <div className="bg-white border-4 border-foreground p-6 shadow-[6px_6px_0px_theme(colors.foreground)] flex flex-col gap-3 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 text-foreground">
              <CheckCircle className="w-5 h-5 text-destructive" />
              <span className="text-sm font-black uppercase tracking-wider">Flagged Abnormalities</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-black tracking-tight text-foreground">24</span>
              <span className="text-xs text-foreground font-bold uppercase border border-foreground px-1 bg-destructive/10">16.9% rate</span>
            </div>
          </div>

          <div className="bg-white border-4 border-foreground p-6 shadow-[6px_6px_0px_theme(colors.foreground)] flex flex-col gap-3 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 text-foreground">
              <Clock className="w-5 h-5 text-[#06b6d4]" />
              <span className="text-sm font-black uppercase tracking-wider">Avg Processing Time</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-black tracking-tight text-foreground">1.4s</span>
              <span className="text-xs text-green-600 font-bold uppercase border border-green-600 px-1 bg-green-50">-0.2s vs last {timeFilter}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="space-y-4 animate-fade-in-up stagger-2">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold tracking-tight">Recent Analyses</h2>
          <div className="flex gap-2">
            <button className="p-2 border-2 border-foreground bg-white text-foreground hover:bg-foreground hover:text-white transition-colors shadow-[2px_2px_0px_theme(colors.foreground)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none">
              <Filter className="w-4 h-4" />
            </button>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="SEARCH CASE ID..." 
                className="pl-9 pr-4 py-2 bg-white border-2 border-foreground text-sm font-bold uppercase focus:outline-none focus:ring-0 shadow-[2px_2px_0px_theme(colors.foreground)] w-64 placeholder:text-muted-foreground/50"
              />
            </div>
          </div>
        </div>

        <div className="bg-white border-4 border-foreground overflow-hidden shadow-[6px_6px_0px_theme(colors.foreground)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#FDFBF7] text-foreground border-b-4 border-foreground">
              <tr>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs">ID</th>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs">Patient</th>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs">Type</th>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs">Findings</th>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs">Status</th>
                <th className="px-4 py-4 font-black uppercase tracking-wider text-xs text-right">Time</th>
                <th className="px-4 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y-2 divide-foreground/20">
              {recentActivity.map((row) => (
                  <tr 
                    key={row.id} 
                    onClick={() => setSelectedCase(row)}
                    className="hover:bg-foreground/5 transition-colors group cursor-pointer"
                  >
                  <td className="px-4 py-4 font-bold text-foreground">{row.id}</td>
                  <td className="px-4 py-4 font-semibold">{row.patient}</td>
                  <td className="px-4 py-4 font-semibold">{row.type}</td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex items-center px-2 py-1 border-2 text-xs font-bold uppercase ${
                      row.findings.includes('Abnormal') ? 'border-destructive bg-destructive/10 text-destructive' :
                      row.findings.includes('Normal') ? 'border-green-600 bg-green-50 text-green-700' :
                      'border-warning bg-warning/10 text-warning'
                    }`}>
                      {row.findings}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="flex items-center gap-2 font-bold uppercase text-xs tracking-wider">
                      <div className={`w-3 h-3 border-2 border-foreground ${row.status === 'Completed' ? 'bg-green-500' : 'bg-warning'}`}></div>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right font-medium text-muted-foreground">{row.date}</td>
                  <td className="px-4 py-4 text-right">
                    <button className="p-1.5 text-foreground hover:bg-foreground hover:text-white border-2 border-transparent hover:border-foreground transition-all">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-4 border-t-4 border-foreground bg-[#FDFBF7] text-center">
            <Link href="/history" className="text-sm text-foreground hover:underline font-black uppercase tracking-widest">
              View all history
            </Link>
          </div>
        </div>
      </div>

      <CaseSummaryPanel 
        data={selectedCase} 
        onClose={() => setSelectedCase(null)} 
      />
    </div>
  );
}
