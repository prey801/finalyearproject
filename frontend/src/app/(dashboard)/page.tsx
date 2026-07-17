'use client';

import Link from 'next/link';
import { Activity, ImageIcon, CheckCircle, Clock, Search, Filter, MoreVertical, FileText, ChevronRight, AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { CaseSummaryPanel, CaseData } from '@/components/shared/CaseSummaryPanel';
import { getAnalysisHistory } from '@/lib/api';

const MOCK_ACTIVITY: CaseData[] = [
  { id: 'AN-2094', date: '10 min ago', patient: 'P-8472', type: 'Blood Smear', status: 'Completed', findings: 'Abnormal (2 flags)' },
  { id: 'AN-2093', date: '1 hr ago', patient: 'P-9102', type: 'Tissue Biopsy', status: 'Completed', findings: 'Normal' },
  { id: 'AN-2092', date: '2 hrs ago', patient: 'P-3321', type: 'Blood Smear', status: 'Review Required', findings: 'Inconclusive' },
  { id: 'AN-2091', date: '4 hrs ago', patient: 'P-1149', type: 'Bone Marrow', status: 'Completed', findings: 'Normal' },
];

export default function Home() {
  const [timeFilter, setTimeFilter] = useState('today');
  const [selectedCase, setSelectedCase] = useState<CaseData | null>(null);
  const [recentActivity, setRecentActivity] = useState<CaseData[]>(MOCK_ACTIVITY);
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
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2"
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
          <div className="flex bg-card border border-border rounded-md p-1">
            {['today', 'week', 'month', 'all'].map(filter => (
              <button
                key={filter}
                onClick={() => setTimeFilter(filter)}
                className={`px-3 py-1 text-sm rounded-sm font-medium capitalize transition-colors ${
                  timeFilter === filter 
                    ? 'bg-primary/20 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in-up stagger-1">
          <div className="bg-card border border-border p-5 rounded-lg shadow-sm flex flex-col gap-3 hover-lift">
            <div className="flex items-center gap-3 text-muted-foreground">
              <ImageIcon className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium">Images Analyzed</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold tracking-tight text-foreground">142</span>
              <span className="text-xs text-green-500 font-medium">+12% vs last {timeFilter}</span>
            </div>
          </div>
          
          <div className="bg-card border border-border p-5 rounded-lg shadow-sm flex flex-col gap-3 hover-lift">
            <div className="flex items-center gap-3 text-muted-foreground">
              <CheckCircle className="w-5 h-5 text-destructive" />
              <span className="text-sm font-medium">Flagged Abnormalities</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold tracking-tight text-foreground">24</span>
              <span className="text-xs text-muted-foreground font-medium">16.9% rate</span>
            </div>
          </div>

          <div className="bg-card border border-border p-5 rounded-lg shadow-sm flex flex-col gap-3 hover-lift">
            <div className="flex items-center gap-3 text-muted-foreground">
              <Clock className="w-5 h-5 text-accent" />
              <span className="text-sm font-medium">Avg Processing Time</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold tracking-tight text-foreground">1.4s</span>
              <span className="text-xs text-green-500 font-medium">-0.2s vs last {timeFilter}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="space-y-4 animate-fade-in-up stagger-2">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold tracking-tight">Recent Analyses</h2>
          <div className="flex gap-2">
            <button className="p-2 border border-border rounded-md text-muted-foreground hover:bg-card hover:text-foreground transition-colors">
              <Filter className="w-4 h-4" />
            </button>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search case ID..." 
                className="pl-9 pr-4 py-2 bg-card border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 w-64"
              />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg overflow-hidden shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50 text-muted-foreground border-b border-border">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Patient</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Findings</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium text-right">Time</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recentActivity.map((row) => (
                  <tr 
                    key={row.id} 
                    onClick={() => setSelectedCase(row)}
                    className="hover:bg-muted/30 transition-colors group cursor-pointer hover-lift relative"
                  >
                  <td className="px-4 py-3 font-medium text-foreground">{row.id}</td>
                  <td className="px-4 py-3">{row.patient}</td>
                  <td className="px-4 py-3">{row.type}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      row.findings.includes('Abnormal') ? 'bg-destructive/10 text-destructive' :
                      row.findings.includes('Normal') ? 'bg-green-500/10 text-green-500' :
                      'bg-warning/10 text-warning'
                    }`}>
                      {row.findings}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1.5">
                      <div className={`w-2 h-2 rounded-full ${row.status === 'Completed' ? 'bg-green-500' : 'bg-warning'}`}></div>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-muted-foreground">{row.date}</td>
                  <td className="px-4 py-3 text-right">
                    <button className="p-1.5 text-muted-foreground hover:text-primary rounded opacity-0 group-hover:opacity-100 transition-opacity">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-3 border-t border-border bg-muted/20 text-center">
            <Link href="/history" className="text-sm text-primary hover:underline font-medium">
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
