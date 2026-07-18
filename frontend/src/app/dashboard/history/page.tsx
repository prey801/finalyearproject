'use client';

import { useEffect, useState } from 'react';
import { Search, Filter, FolderSearch, ChevronLeft, ChevronRight, FileX2 } from 'lucide-react';
import Link from 'next/link';
import { CaseSummaryPanel, CaseData } from '@/components/shared/CaseSummaryPanel';
import { getAnalysisHistory } from '@/lib/api';



export default function HistoryPage() {
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCase, setSelectedCase] = useState<CaseData | null>(null);
  const [history, setHistory] = useState<CaseData[]>([]);
  
  useEffect(() => {
    getAnalysisHistory(0, 100)
      .then(data => {
        if (data && data.length > 0) {
          setHistory(data.map(item => ({
            id: item.sample_id,
            date: 'Recent',
            patient: item.patient_id,
            type: item.specimen_type,
            status: item.review_required ? 'Review Required' : 'Completed',
            findings: item.prediction?.toLowerCase() === 'malaria' ? `Abnormal (${item.parasitemia}%)` : 'Normal'
          })));
        }
      })
      .catch(err => console.error("Failed to fetch full history:", err));
  }, []);

  // Toggle this to see empty state
  const isEmpty = history.length === 0;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 relative">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Analysis History</h1>
          <p className="text-muted-foreground mt-1">Review past digital microscopy cases and AI findings</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row justify-between gap-4 items-center bg-card p-4 rounded-xl border border-border shadow-sm">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0 hide-scrollbar">
          {['All', 'Completed', 'Review Required', 'Abnormal', 'Failed'].map(filter => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-3 py-1.5 text-sm rounded-full font-medium whitespace-nowrap transition-colors border ${
                activeFilter === filter 
                  ? 'bg-primary/20 border-primary/30 text-primary' 
                  : 'bg-transparent border-transparent text-muted-foreground hover:bg-muted'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
        
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button className="p-2 border border-border rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors hidden sm:block">
            <Filter className="w-4 h-4" />
          </button>
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search ID, Patient, or Type..." 
              className="pl-9 pr-4 py-2 w-full bg-muted/50 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>
      </div>

      {isEmpty ? (
        <div className="bg-card border border-border rounded-xl p-16 flex flex-col items-center justify-center text-center shadow-sm">
          <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mb-6">
            <FileX2 className="w-10 h-10 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">No Past Analyses Found</h3>
          <p className="text-muted-foreground max-w-sm mb-8">
            You haven't run any digital microscopy analyses yet. Start your first case to see the history here.
          </p>
          <Link 
            href="/dashboard/analyze" 
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors"
          >
            Start your first analysis &rarr;
          </Link>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-muted/50 text-muted-foreground border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-medium">Case ID</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium">Patient Ref</th>
                  <th className="px-6 py-4 font-medium">Specimen Type</th>
                  <th className="px-6 py-4 font-medium">AI Findings</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((row) => (
                  <tr 
                    key={row.id} 
                    onClick={() => setSelectedCase(row)}
                    className="hover:bg-muted/30 transition-colors group cursor-pointer"
                  >
                    <td className="px-6 py-4 font-medium text-foreground">{row.id}</td>
                    <td className="px-6 py-4 text-muted-foreground">{row.date}</td>
                    <td className="px-6 py-4">{row.patient}</td>
                    <td className="px-6 py-4">{row.type}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                        row.findings.includes('Abnormal') ? 'bg-destructive/10 border-destructive/20 text-destructive' :
                        row.findings.includes('Normal') ? 'bg-green-500/10 border-green-500/20 text-green-500' :
                        'bg-warning/10 border-warning/20 text-warning'
                      }`}>
                        {row.findings}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          row.status === 'Completed' ? 'bg-green-500' : 
                          row.status === 'Failed' ? 'bg-destructive' : 'bg-warning'
                        }`}></div>
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <FolderSearch className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors ml-auto" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="p-4 border-t border-border flex items-center justify-between text-sm text-muted-foreground bg-muted/20">
            <span>Showing 1 to 6 of 142 entries</span>
            <div className="flex items-center gap-1">
              <button className="p-1 border border-border rounded-md hover:bg-card hover:text-foreground transition-colors disabled:opacity-50">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button className="px-3 py-1 bg-primary/20 text-primary border border-primary/30 rounded-md font-medium">1</button>
              <button className="px-3 py-1 hover:bg-card border border-transparent rounded-md transition-colors">2</button>
              <button className="px-3 py-1 hover:bg-card border border-transparent rounded-md transition-colors">3</button>
              <span className="px-2">...</span>
              <button className="p-1 border border-border rounded-md hover:bg-card hover:text-foreground transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      <CaseSummaryPanel 
        data={selectedCase} 
        onClose={() => setSelectedCase(null)} 
      />
    </div>
  );
}
