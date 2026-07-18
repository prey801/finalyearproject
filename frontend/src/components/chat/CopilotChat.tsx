'use client';

import { useState } from 'react';
import { Send, Bot, Sparkles, AlertCircle, Eye, Loader2 } from 'lucide-react';
import { chatWithCopilot } from '@/lib/api';
import { useActiveImageStore } from '@/store/activeImageStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const QUICK_PROMPTS = [
  "Explain classification",
  "Summarize findings",
  "Compare to history"
];

export function CopilotChat() {
  const { analysisResult } = useActiveImageStore();
  
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Clinical Copilot initialized. I have loaded the current slide context. How can I assist you with this analysis?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);


  const handleSend = async (text: string = input) => {
    if (!text.trim() || isLoading) return;
    
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: text }]);
    setInput('');
    setIsLoading(true);
    
    try {
      let context = "No image currently loaded.";
      if (analysisResult) {
        context = `Image Context:
- Prediction: ${analysisResult.prediction} (Confidence: ${analysisResult.confidence.toFixed(1)}%)
- Patient ID: ${analysisResult.patient_id}
- Specimen Type: ${analysisResult.specimen_type}
- Parasitemia Level: ${analysisResult.parasitemia.toFixed(2)}%
- Infected Cells: ${analysisResult.infected_cells} / ${analysisResult.total_cells}
- Quality: ${analysisResult.quality}
- Generated Report: ${analysisResult.report}`;
      }
      
      const reply = await chatWithCopilot(text, context);
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        role: 'assistant', 
        content: reply 
      }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        role: 'assistant', 
        content: "I'm sorry, I encountered an error connecting to the clinical backend. Please try again." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-card relative">
      {/* Header */}
      <div className="p-3 border-b border-border bg-card/95 backdrop-blur shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-primary/20 rounded-md">
            <Sparkles className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h2 className="font-semibold text-sm text-foreground leading-none">Diagnostic Copilot</h2>
            <div className="flex items-center gap-1.5 mt-1">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">MedLM-v2 (Specialized)</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Context Indicator */}
      <div className="bg-muted/30 border-b border-border px-3 py-2 flex items-center gap-2 text-xs text-muted-foreground shrink-0">
        <Eye className="w-3.5 h-3.5" />
        <span>Context: <span className="font-medium text-foreground">
          {analysisResult ? `${analysisResult.specimen_type} (${analysisResult.prediction})` : 'Awaiting Image'}
        </span></span>
      </div>
      
      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[90%] p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-muted text-foreground rounded-l-xl rounded-tr-xl' 
                : 'bg-transparent border border-border text-foreground rounded-r-xl rounded-tl-xl'
            }`}>
              <p className="leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex flex-col items-start">
            <div className="max-w-[90%] p-3 text-sm bg-transparent border border-border text-foreground rounded-r-xl rounded-tl-xl flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <p className="leading-relaxed text-muted-foreground">Analyzing...</p>
            </div>
          </div>
        )}
        {/* Warning Disclaimer in chat */}
        <div className="flex justify-center mt-4 mb-2">
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground bg-muted/50 px-2 py-1 rounded">
            <AlertCircle className="w-3 h-3" />
            <span>AI can make mistakes. Verify clinical findings.</span>
          </div>
        </div>
      </div>
      
      {/* Input Area */}
      <div className="p-3 bg-card border-t border-border shrink-0">
        {/* Quick Prompts */}
        <div className="flex flex-wrap gap-2 mb-3">
          {QUICK_PROMPTS.map(prompt => (
            <button 
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="text-[10px] border border-border hover:border-primary text-muted-foreground hover:text-primary px-2 py-1 rounded-full transition-colors whitespace-nowrap"
            >
              {prompt}
            </button>
          ))}
        </div>
        
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a question..."
            rows={1}
            className="w-full bg-muted/50 border border-border rounded-lg py-2.5 pl-3 pr-10 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all resize-none overflow-hidden min-h-[44px]"
          />
          <button 
            onClick={() => handleSend(input)}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-2 p-1.5 bg-primary disabled:bg-primary/50 disabled:cursor-not-allowed hover:bg-primary/90 text-primary-foreground rounded-md transition"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
