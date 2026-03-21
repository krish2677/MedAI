import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Microscope, ShieldCheck, Zap, Activity } from 'lucide-react'
import ImageUpload from '../components/ImageUpload'
import SymptomInput from '../components/SymptomInput'
import PageTransition from '../components/PageTransition'
import ScanSelector from '../components/ScanSelector'

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
    <PageTransition>
      <div className="min-h-screen bg-bg pb-16 overflow-x-hidden">
        {/* Disclaimer Banner */}
        <div className="bg-warning/10 border-b border-warning/20 text-warning px-4 py-3 text-center text-sm font-medium sticky top-0 z-40 backdrop-blur-sm shadow-sm" data-aos="fade-down">
          ⚠️ AI Medical Diagnosis Assistant is a research demonstration. It is NOT a substitute for professional medical advice.
        </div>

        <main className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 mt-12">
          {/* Top Hero Section: Form on Left, ScanSelector on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* Left Col: Header & Upload Form */}
            <div className="lg:col-span-6 xl:col-span-5 space-y-8" data-aos="fade-right" data-aos-duration="1000">
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-xs font-bold uppercase tracking-wide shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  System Online — Next-Gen AI
                </div>
                <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-slate-800 leading-tight tracking-tight">
                  AI-Powered <br />
                  <span className="gradient-text drop-shadow-sm">Medical Analysis</span>
                </h1>
                <p className="text-lg text-slate-600 text-balance leading-relaxed">
                  Select a scan modality, upload the medical image, and describe the patient's symptoms.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="card p-6 md:p-8 space-y-6 hover:shadow-card-hover transition-shadow duration-500 relative z-20">
                {/* Visual Feedback of Selected Modality */}
                <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                  <span className="text-sm font-bold text-slate-700 uppercase tracking-widest">Active Scan Region</span>
                  <span className="px-3 py-1 bg-teal-50 text-teal-700 font-bold text-sm rounded-full border border-teal-200 shadow-sm animate-pulse">
                     {modality === 'chest_xray' ? '🫁 Chest X-Ray' : modality === 'skin' ? '🔬 Skin Lesion' : '👁️ Retinal Scan'}
                  </span>
                </div>

                {/* Image Upload */}
                <ImageUpload onImageSelected={setImage} selectedImage={image} />

                {/* Symptom Input (Voice Enabled) */}
                <SymptomInput symptoms={symptoms} setSymptoms={setSymptoms} />

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!isFormValid || loading}
                  className={`w-full py-4 rounded-xl text-white font-bold text-lg flex items-center justify-center gap-2 transition-all duration-300 ${
                    !isFormValid || loading 
                      ? 'bg-slate-300 shadow-none cursor-not-allowed text-slate-500' 
                      : 'bg-medical-gradient hover:opacity-90 hover:shadow-glow transform hover:-translate-y-1'
                  }`}
                >
                  {loading ? (
                     <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Running Deep Analysis...
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

            {/* Right Col: Premium Scan Selector */}
            <div className="lg:col-span-6 xl:col-span-7 lg:sticky lg:top-24 hidden lg:flex flex-col justify-center bg-transparent rounded-[32px] p-2 xl:p-8" data-aos="zoom-in" data-aos-duration="1200" data-aos-delay="200">
               <div className="mb-8 px-2">
                 <h2 className="text-3xl font-heading font-extrabold text-slate-800 tracking-tight">Select Modality</h2>
                 <p className="text-slate-500 font-medium mt-2 leading-relaxed">Choose the specific type of medical scan you are uploading to automatically calibrate the deep learning models.</p>
               </div>
               <ScanSelector selected={modality} onSelect={setModality} />
            </div>
            
            {/* Mobile Fallback selector (visible only on small screens) */}
            <div className="lg:hidden col-span-1 border-t border-slate-200 pt-8" data-aos="fade-up">
               <h3 className="font-heading font-bold text-slate-700 mb-4 text-center">Or select scan type manually:</h3>
               <div className="grid grid-cols-3 gap-2">
                  {['chest_xray', 'skin', 'retina'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setModality(type)}
                      className={`py-3 px-2 rounded-lg text-xs md:text-sm font-bold transition-all ${
                        modality === type 
                          ? 'bg-teal-500 text-white shadow-md' 
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {type === 'chest_xray' ? '🫁 Chest' : type === 'skin' ? '🔬 Skin' : '👁️ Retina'}
                    </button>
                  ))}
                </div>
            </div>

          </div>

          {/* Bottom Section: How it Works */}
          <div className="mt-32 border-t border-slate-200 pt-16">
            <div className="text-center max-w-2xl mx-auto mb-12" data-aos="fade-up">
              <h2 className="text-3xl font-heading font-extrabold text-slate-800 tracking-tight">Enterprise-Grade Architecture</h2>
              <p className="text-slate-500 mt-4 leading-relaxed">Our pipeline combines multiple cutting-edge AI models for maximum accuracy and clinical reasoning.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white/80 backdrop-blur-md rounded-[20px] p-8 shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group" data-aos="fade-up" data-aos-delay="100">
                <div className="w-14 h-14 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                  <Scan size={28} />
                </div>
                <h4 className="font-heading font-bold text-slate-800 text-xl mb-3">1. Vision CNN</h4>
                <p className="text-slate-500 text-sm leading-relaxed">
                  An EfficientNet CNN deeply analyzes your medical scan to detect highly complex visual anomalies.
                </p>
              </div>

              <div className="bg-white/80 backdrop-blur-md rounded-[20px] p-8 shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group" data-aos="fade-up" data-aos-delay="200">
                <div className="w-14 h-14 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center mb-6 group-hover:bg-teal-500 group-hover:text-white transition-colors duration-300">
                  <Activity size={28} />
                </div>
                <h4 className="font-heading font-bold text-slate-800 text-xl mb-3">2. Clinical NLP</h4>
                <p className="text-slate-500 text-sm leading-relaxed">
                  A BioBERT model heavily extracts vital medical entities from your text, weighting symptom probabilities.
                </p>
              </div>

              <div className="bg-white/80 backdrop-blur-md rounded-[20px] p-8 shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 group" data-aos="fade-up" data-aos-delay="300">
                <div className="w-14 h-14 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center mb-6 group-hover:bg-purple-500 group-hover:text-white transition-colors duration-300">
                  <Zap size={28} />
                </div>
                <h4 className="font-heading font-bold text-slate-800 text-xl mb-3">3. GenAI Fusion</h4>
                <p className="text-slate-500 text-sm leading-relaxed">
                  Multimodal scores are fused and sent to a blazing-fast Llama 3 LLM pipeline to generate a grounded report.
                </p>
              </div>
            </div>
            
            <div className="mt-12 p-6 bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl text-center shadow-2xl" data-aos="zoom-in" data-aos-delay="400">
              <div className="flex items-center justify-center gap-2 text-white font-bold mb-2">
                <ShieldCheck size={20} className="text-green-400"/> Absolute Data Privacy
              </div>
              <p className="text-sm text-slate-300 leading-relaxed max-w-3xl mx-auto">
                Images are processed fully in memory and never stored permanently on our servers. Designed for utmost patient confidentiality.
              </p>
            </div>
          </div>
        </main>
      </div>
    </PageTransition>
  )
}

function Scan(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
      <path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/>
    </svg>
  );
}
