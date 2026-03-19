import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, FileBarChart, BrainCircuit } from 'lucide-react'
import HeatmapViewer from '../components/HeatmapViewer'
import ConfidenceChart from '../components/ConfidenceChart'
import DiagnosisReport from '../components/DiagnosisReport'
import UrgencyBadge from '../components/UrgencyBadge'
import ChatBox from '../components/ChatBox'

export default function Results({ result, error, loading, reportLoading }) {
  const navigate = useNavigate()

  useEffect(() => {
    // Redirect to home if no valid context exists
    if (!result && !loading && !error) {
      navigate('/')
    }
  }, [result, loading, error, navigate])

  if (error) {
    return (
      <div className="min-h-screen bg-bg flex flex-col items-center justify-center p-4">
        <div className="card max-w-md w-full p-8 text-center space-y-4">
          <div className="w-16 h-16 mx-auto bg-red-100 text-danger rounded-full flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          </div>
          <h2 className="text-xl font-bold text-slate-800">Analysis Failed</h2>
          <p className="text-slate-600 border-l-4 border-danger bg-red-50 p-3 text-left text-sm rounded-r-md">
            {error || "An unknown error occurred during analysis."}
          </p>
          <button onClick={() => navigate('/')} className="btn-primary w-full mt-4">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!result && loading) {
     return (
        <div className="min-h-screen bg-bg flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
               <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
               <p className="text-lg font-medium text-slate-600 animate-pulse">Running Multimodal AI Diagnosis...</p>
            </div>
        </div>
     )
  }

  if (!result) return null

  // Format diagnosis context for ChatBox
  const diagContext = result.fusion_scores
    .map(s => `${s.condition} (${(s.final_score*100).toFixed(1)}%)`)
    .join(', ')

  return (
    <div className="min-h-screen bg-bg">
      {/* Top Nav */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-[1400px] mx-auto px-4 h-16 flex items-center justify-between">
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors font-medium text-sm"
          >
            <ChevronLeft size={18} /> New Patient Scan
          </button>
          
          <div className="flex items-center gap-2">
             <BrainCircuit size={18} className="text-primary-500" />
             <span className="font-heading font-bold text-slate-800">Analysis Complete</span>
          </div>
        </div>
      </nav>

      <main className="max-w-[1400px] mx-auto px-4 py-8">
        
        {/* Header Summary */}
        <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-heading font-extrabold text-slate-800 mb-2">Diagnostic Results</h1>
            <p className="text-slate-500 flex items-center gap-2">
              <FileBarChart size={16} /> Patient Report Generated
            </p>
          </div>
          <UrgencyBadge level={result.urgency_level} />
        </header>

        {/* 3-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Col 1: Visual Explanation (Heatmap) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="card p-5">
              <h3 className="section-title">Visual Explanation</h3>
              <HeatmapViewer 
                originalSrc={result.imageUrl} 
                heatmapBase64={result.heatmap_base64} 
              />
            </div>

            <div className="card p-5 border-l-4 border-l-primary-500">
               <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">Extracted Symptoms (NLP)</h3>
               <div className="flex flex-wrap gap-2">
                 {result.extracted_symptoms?.length > 0 ? (
                    result.extracted_symptoms.map((s, i) => (
                      <span key={i} className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-sm border border-slate-200">
                        {s}
                      </span>
                    ))
                 ) : (
                    <span className="text-sm text-slate-400 italic">No specific medical terms extracted.</span>
                 )}
               </div>
            </div>
          </div>
          
          {/* Col 2: Confidence Scores */}
          <div className="lg:col-span-4 space-y-6">
            <div className="card p-5 h-full min-h-[400px]">
              <h3 className="section-title">Prediction Confidence</h3>
              <p className="text-sm text-slate-500 mb-6">
                Ensemble fusion of visual (CNN) and clinical (NLP) models.
              </p>
              <ConfidenceChart predictions={result.fusion_scores} />
            </div>
          </div>

          {/* Col 3: LLM Generated Report */}
          <div className="lg:col-span-4 space-y-6">
             {/* Report Generator Component */}
             <div className="lg:h-[calc(100vh-250px)] min-h-[500px]">
                <DiagnosisReport 
                  report={result.report} 
                  sourcesUsed={result.sourcesUsed} 
                  loading={reportLoading} 
                />
             </div>
          </div>
          
        </div>

        {/* Global Chat Box Row */}
        <div className="mt-8 max-w-4xl mx-auto">
           <ChatBox diagnosisContext={diagContext} />
        </div>

      </main>
    </div>
  )
}
