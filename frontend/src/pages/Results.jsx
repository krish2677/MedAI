import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, FileBarChart, BrainCircuit } from 'lucide-react'
import HeatmapViewer from '../components/HeatmapViewer'
import ConfidenceChart from '../components/ConfidenceChart'
import DiagnosisReport from '../components/DiagnosisReport'
import UrgencyBadge from '../components/UrgencyBadge'
import ChatBox from '../components/ChatBox'
import PageTransition from '../components/PageTransition'
import SpecialistFinder from '../components/SpecialistFinder'

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
      <PageTransition>
        <div className="min-h-screen bg-bg flex flex-col items-center justify-center p-4">
          <div className="card max-w-md w-full p-8 text-center space-y-4" data-aos="zoom-in">
            <div className="w-16 h-16 mx-auto bg-red-100 text-danger rounded-full flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            </div>
            <h2 className="text-2xl font-heading font-bold text-slate-800">Analysis Failed</h2>
            <p className="text-slate-600 border-l-4 border-danger bg-red-50 p-4 text-left text-sm rounded-r-md font-medium shadow-inner">
              {error || "An unknown error occurred during analysis."}
            </p>
            <button onClick={() => navigate('/')} className="btn-primary w-full mt-4 hover:shadow-lg transition-all transform hover:-translate-y-1">
              Try Again
            </button>
          </div>
        </div>
      </PageTransition>
    )
  }

  if (!result && loading) {
     return (
       <PageTransition>
          <div className="min-h-screen bg-bg flex items-center justify-center">
              <div className="flex flex-col items-center gap-6" data-aos="fade-up">
                 <div className="relative w-20 h-20">
                   <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
                   <div className="absolute inset-0 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                   <div className="absolute inset-0 flex items-center justify-center text-primary-500 animate-pulse">
                     <BrainCircuit size={24} />
                   </div>
                 </div>
                 <p className="text-xl font-heading font-bold text-slate-700 animate-pulse drop-shadow-sm">Running Medical AI Diagnosis...</p>
                 <p className="text-sm text-slate-500">Processing visual and textual data. This may take a moment.</p>
              </div>
          </div>
       </PageTransition>
     )
  }

  if (!result) return null

  // Format diagnosis context for ChatBox
  const diagContext = `
Diagnosis Scores:
${result.fusion_scores.map(s => `- ${s.condition} (${(s.final_score * 100).toFixed(1)}%)`).join('\n')}

Extracted Symptoms:
${result.extracted_symptoms?.join(', ') || 'None provided'}

Detailed Generated Report:
${result.report || 'The detailed report is currently being generated or is unavailable.'}
`.trim()

  return (
    <PageTransition>
      <div className="min-h-screen bg-bg overflow-x-hidden">
        {/* Top Nav (Replaced by Global Navbar, keeping sub-header for navigation) */}
        <div className="bg-white/80 backdrop-blur-md border-b border-slate-200/50 relative z-30 shadow-sm" data-aos="fade-down">
          <div className="max-w-[1400px] mx-auto px-4 h-12 flex items-center justify-between">
            <button 
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors font-bold text-sm"
            >
              <ChevronLeft size={18} /> Run New Patient Scan
            </button>
            <div className="flex items-center gap-2">
               <BrainCircuit size={18} className="text-primary-500" />
               <span className="font-heading font-bold text-slate-800 text-sm tracking-wide">Analysis Complete</span>
            </div>
          </div>
        </div>

        <main className="max-w-[1400px] mx-auto px-4 py-8">
          
          {/* Header Summary */}
          <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4" data-aos="fade-right">
            <div>
              <h1 className="text-4xl font-heading font-extrabold text-slate-800 mb-2 tracking-tight">Diagnostic Results</h1>
              <p className="text-slate-500 flex items-center gap-2 font-medium">
                <FileBarChart size={16} className="text-primary-500" /> Grounded Patient Report Generated
              </p>
            </div>
            <div data-aos="zoom-in" data-aos-delay="200">
              <UrgencyBadge level={result.urgency_level} />
            </div>
          </header>

          {/* 3-Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Col 1: Visual Explanation (Heatmap) */}
            <div className="lg:col-span-4 space-y-6" data-aos="fade-up" data-aos-delay="100">
              <div className="card p-6 border-t-4 border-t-primary-500 hover:-translate-y-1 transition-transform duration-300">
                <h3 className="section-title">Visual AI Heatmap</h3>
                <p className="text-sm text-slate-500 mb-4">Grad-CAM visualization of the areas the Vision Model focused on.</p>
                <HeatmapViewer 
                  originalSrc={result.imageUrl} 
                  heatmapBase64={result.heatmap_base64} 
                />
              </div>

              <div className="card p-6 border-l-4 border-l-teal-500 hover:shadow-lg transition-shadow duration-300">
                 <h3 className="text-sm font-extrabold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                   <BrainCircuit size={16} className="text-teal-500"/> Extracted Symptoms (NLP)
                 </h3>
                 <div className="flex flex-wrap gap-2">
                   {result.extracted_symptoms?.length > 0 ? (
                      result.extracted_symptoms.map((s, i) => (
                        <span key={i} className="px-3 py-1.5 bg-slate-100/80 text-slate-700 font-medium rounded-md text-sm border border-slate-200/60 shadow-sm">
                          {s}
                        </span>
                      ))
                   ) : (
                      <span className="text-sm text-slate-400 italic">No specific medical terms extracted.</span>
                   )}
                 </div>
              </div>

              {/* Dynamic Specialist Finder Map Link */}
              <div data-aos="fade-up" data-aos-delay="150">
                <SpecialistFinder scores={result.fusion_scores} />
              </div>
            </div>
            
            {/* Col 2: Confidence Scores */}
            <div className="lg:col-span-4 space-y-6" data-aos="fade-up" data-aos-delay="200">
              <div className="card p-6 h-full min-h-[400px] border-t-4 border-t-blue-500 hover:-translate-y-1 transition-transform duration-300">
                <h3 className="section-title">Ensemble Confidence</h3>
                <p className="text-sm text-slate-500 mb-6 font-medium">
                  Algorithmic fusion of visual (CNN) and clinical (NLP) models.
                </p>
                <ConfidenceChart predictions={result.fusion_scores} />
              </div>
            </div>

            {/* Col 3: LLM Generated Report */}
            <div className="lg:col-span-4 space-y-6" data-aos="fade-left" data-aos-delay="300">
               <div className="lg:h-[calc(100vh-250px)] min-h-[500px] card overflow-hidden border-t-4 border-t-purple-500 shadow-glow hover:shadow-lg transition-shadow duration-300">
                  <div className="h-full bg-gradient-to-b from-slate-50 to-white">
                    <DiagnosisReport 
                      report={result.report} 
                      sourcesUsed={result.sourcesUsed} 
                      loading={reportLoading} 
                    />
                  </div>
               </div>
            </div>
            
          </div>

          {/* Global Chat Box Row */}
          <div className="mt-12 max-w-4xl mx-auto" data-aos="fade-up" data-aos-offset="0">
             <ChatBox diagnosisContext={diagContext} />
          </div>

        </main>
      </div>
    </PageTransition>
  )
}
