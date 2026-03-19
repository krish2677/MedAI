import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Microscope, ShieldCheck, Zap, Activity } from 'lucide-react'
import ImageUpload from '../components/ImageUpload'
import SymptomInput from '../components/SymptomInput'

export default function Home({ onAnalyze, loading }) {
  const navigate = useNavigate()
  const [image, setImage] = useState(null)
  const [symptoms, setSymptoms] = useState('')
  const [modality, setModality] = useState('chest_xray')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!image || !symptoms) return
    
    // Pass data back up to App/useAnalysis
    await onAnalyze(image, symptoms, modality)
    navigate('/results')
  }

  const isFormValid = image && symptoms.length >= 5

  return (
    <div className="min-h-screen bg-bg pb-16">
      {/* Disclaimer Banner */}
      <div className="bg-warning/10 border-b border-warning/20 text-warning px-4 py-3 text-center text-sm font-medium sticky top-0 z-50 backdrop-blur-sm">
        ⚠️ AI Medical Diagnosis Assistant is a research demonstration. It is NOT a substitute for professional medical advice.
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Header & Upload Form */}
          <div className="lg:col-span-7 space-y-8 animate-slide-up">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-xs font-bold uppercase tracking-wide">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                System Online — v1.0
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-extrabold text-slate-800 leading-tight">
                AI-Powered <br className="hidden md:block"/>
                <span className="gradient-text">Medical Analysis</span>
              </h1>
              <p className="text-lg text-slate-600 max-w-2xl text-balance">
                Upload a medical scan and describe your symptoms. Our multimodal AI engine combines computer vision and NLP to generate a detailed, explainable diagnostic report.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="card p-6 md:p-8 space-y-6">
              {/* Modality Selector */}
              <div>
                <label className="text-sm font-semibold text-slate-700 block mb-3">Scan Type</label>
                <div className="grid grid-cols-3 gap-3">
                  {['chest_xray', 'skin', 'retina'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setModality(type)}
                      className={`py-3 px-2 rounded-lg text-sm font-medium transition-all ${
                        modality === type 
                          ? 'bg-primary-50 border-2 border-primary-500 text-primary-800 shadow-sm' 
                          : 'bg-slate-50 border-2 border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900 cursor-pointer'
                      }`}
                    >
                      {type === 'chest_xray' ? 'Chest X-Ray' : type === 'skin' ? 'Skin Lesion' : 'Retinal Scan'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Image Upload */}
              <ImageUpload onImageSelected={setImage} selectedImage={image} />

              {/* Symptom Input */}
              <SymptomInput symptoms={symptoms} setSymptoms={setSymptoms} />

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!isFormValid || loading}
                className={`w-full py-4 rounded-xl text-white font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-glow ${
                  !isFormValid || loading 
                    ? 'bg-slate-300 shadow-none cursor-not-allowed text-slate-500' 
                    : 'bg-medical-gradient hover:opacity-95 transform hover:-translate-y-0.5'
                }`}
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing Data...
                  </>
                ) : (
                  <>
                    <Microscope size={20} />
                    Run AI Diagnosis
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Feature Highlight Cards */}
          <div className="lg:col-span-5 space-y-6 lg:pl-8">
            <h3 className="font-heading font-bold text-xl text-slate-800 mb-6">How it works</h3>
            
            <div className="bg-white rounded-[16px] p-6 shadow-sm border border-slate-100 hover:border-primary-100 transition-colors flex gap-4">
              <div className="shrink-0 w-12 h-12 rounded-full bg-blue-50 text-primary-600 flex items-center justify-center">
                <Scan size={24} />
              </div>
              <div>
                <h4 className="font-heading font-bold text-slate-800 text-lg">1. Visual Analysis</h4>
                <p className="text-slate-500 text-sm mt-1 leading-relaxed">
                  An EfficientNet-B4 CNN analyzes your medical scan to detect visual patterns associated with specific conditions.
                </p>
              </div>
            </div>

            <div className="bg-white rounded-[16px] p-6 shadow-sm border border-slate-100 hover:border-primary-100 transition-colors flex gap-4">
              <div className="shrink-0 w-12 h-12 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center">
                <Activity size={24} />
              </div>
              <div>
                <h4 className="font-heading font-bold text-slate-800 text-lg">2. Symptom Mapping</h4>
                <p className="text-slate-500 text-sm mt-1 leading-relaxed">
                  A BioBERT NLP model extracts key medical entities from your text and calculates differential probabilities.
                </p>
              </div>
            </div>

            <div className="bg-white rounded-[16px] p-6 shadow-sm border border-slate-100 hover:border-primary-100 transition-colors flex gap-4">
              <div className="shrink-0 w-12 h-12 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center">
                <Zap size={24} />
              </div>
              <div>
                <h4 className="font-heading font-bold text-slate-800 text-lg">3. Multimodal Fusion</h4>
                <p className="text-slate-500 text-sm mt-1 leading-relaxed">
                  Scores are fused and sent to a RAG pipeline to generate a grounded, comprehensible diagnostic report.
                </p>
              </div>
            </div>
            
            <div className="mt-8 p-5 bg-slate-50 rounded-xl border border-slate-200">
              <div className="flex items-center gap-2 text-slate-700 font-semibold mb-2">
                <ShieldCheck size={18} className="text-green-500"/> Privacy Focused
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                Images are processed in memory and never stored permanently on our servers. The entire prediction process occurs securely within an isolated container.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

// Ensure the Scan icon is defined or imported, doing it here in file for quick fix since I missed it above:
function Scan(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
      <path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/>
    </svg>
  );
}
