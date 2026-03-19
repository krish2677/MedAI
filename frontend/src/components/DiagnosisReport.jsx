import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FileText, Printer, FileSearch } from 'lucide-react'

export default function DiagnosisReport({ report, sourcesUsed, loading }) {
  if (loading) {
    return (
      <div className="card p-6 h-full min-h-[400px] flex flex-col pt-12">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div>
            <div className="h-5 w-48 bg-slate-200 rounded animate-pulse mb-2"></div>
            <div className="h-3 w-32 bg-slate-100 rounded animate-pulse"></div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="h-4 w-full bg-slate-100 rounded animate-pulse"></div>
          <div className="h-4 w-full bg-slate-100 rounded animate-pulse"></div>
          <div className="h-4 w-3/4 bg-slate-100 rounded animate-pulse"></div>
          
          <div className="h-6 w-1/3 bg-slate-200 rounded animate-pulse mt-8 mb-4"></div>
          <div className="h-4 w-full bg-slate-100 rounded animate-pulse"></div>
          <div className="h-4 w-5/6 bg-slate-100 rounded animate-pulse"></div>
          
          <div className="h-6 w-1/4 bg-slate-200 rounded animate-pulse mt-8 mb-4"></div>
          <div className="flex gap-2">
            <div className="h-8 w-8 bg-slate-100 rounded-full animate-pulse"></div>
            <div className="h-8 w-32 bg-slate-100 rounded-full animate-pulse"></div>
            <div className="h-8 w-24 bg-slate-100 rounded-full animate-pulse"></div>
          </div>
        </div>
        
        <div className="mt-auto pt-8 flex items-center justify-center text-sm text-slate-400 gap-2">
          <FileSearch size={16} className="animate-pulse" />
          Analyzing medical literature via RAG pipeline...
        </div>
      </div>
    )
  }

  if (!report) return null

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="card flex flex-col h-full print:shadow-none print:border-none print:p-0 relative">
      <div className="p-6 md:p-8 flex-1 overflow-y-auto min-h-[500px] print:overflow-visible">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-50 rounded-lg text-primary-700">
              <FileText size={24} />
            </div>
            <div>
              <h2 className="font-heading font-bold text-xl text-slate-800">
                Clinical AI Report
              </h2>
              <p className="text-sm text-slate-500 flex items-center gap-1.5 mt-0.5">
                <span className="w-2 h-2 rounded-full bg-teal-500"></span>
                Grounded in {sourcesUsed} medical literature sources
              </p>
            </div>
          </div>
          
          <button 
            onClick={handlePrint}
            className="p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors print:hidden"
            title="Print or Save as PDF"
          >
            <Printer size={20} />
          </button>
        </div>

        <div className="prose prose-slate prose-sm md:prose-base max-w-none prose-headings:font-heading prose-headings:text-slate-800 prose-p:text-slate-600 prose-li:text-slate-600 prose-strong:text-slate-800 prose-a:text-primary-600 hover:prose-a:text-primary-800">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
