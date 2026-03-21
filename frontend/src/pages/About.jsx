import React from 'react';
import PageTransition from '../components/PageTransition';
import { ShieldAlert, HeartPulse, Server } from 'lucide-react';

export default function About() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-bg py-16 px-4">
        <div className="max-w-5xl mx-auto">
          
          <div className="text-center mb-16" data-aos="fade-down">
            <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-slate-800 mb-4 tracking-tight">
              About Med<span className="text-primary-500">AI</span>
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Our mission is to make preliminary diagnostic screening accessible, transparent, and extremely fast using state-of-the-art Artificial Intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card p-8 flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300" data-aos="fade-up" data-aos-delay="0">
              <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-6">
                <HeartPulse size={32} />
              </div>
              <h3 className="font-heading font-bold text-xl mb-3">Empowering Patients</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                By translating complex medical images and jargon into understandable language, we empower patients to have more informed conversations with their healthcare providers.
              </p>
            </div>

            <div className="card p-8 flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300" data-aos="fade-up" data-aos-delay="100">
              <div className="w-16 h-16 bg-teal-50 text-teal-600 rounded-full flex items-center justify-center mb-6">
                <ShieldAlert size={32} />
              </div>
              <h3 className="font-heading font-bold text-xl mb-3">Ethical AI Guardrails</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Our system is strictly hard-coded not to prescribe medication or definitively diagnose. Every component is designed around safety, prompting users to seek professional advice.
              </p>
            </div>

            <div className="card p-8 flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300" data-aos="fade-up" data-aos-delay="200">
              <div className="w-16 h-16 bg-purple-50 text-purple-600 rounded-full flex items-center justify-center mb-6">
                <Server size={32} />
              </div>
              <h3 className="font-heading font-bold text-xl mb-3">Absolute Privacy</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                We do not store your medical scans or symptom data persistently. Analyzed data is processed completely in-memory and wiped instantly after your session closes.
              </p>
            </div>
          </div>

          <div className="mt-16 bg-primary-900 rounded-[20px] p-8 md:p-12 text-white relative overflow-hidden" data-aos="zoom-in" data-aos-delay="300">
            <div className="absolute top-0 right-0 -transtale-y-1/2 translate-x-1/3 w-64 h-64 bg-teal-400 opacity-20 blur-3xl rounded-full"></div>
            <div className="absolute bottom-0 left-0 translate-y-1/3 -translate-x-1/3 w-80 h-80 bg-blue-500 opacity-20 blur-3xl rounded-full"></div>
            
            <div className="relative z-10 max-w-2xl">
              <h2 className="text-3xl font-heading font-bold mb-4">A Collaborative Tool, Not a Doctor</h2>
              <p className="text-primary-100 text-lg mb-6 leading-relaxed">
                MedAI is built as a highly sophisticated triage tool. While it uses models that equal clinical benchmarks, it cannot replicate the holistic assessment of a human doctor trained in medicine. 
              </p>
              <button onClick={() => window.history.back()} className="px-6 py-3 bg-white text-primary-900 rounded-full font-bold hover:bg-slate-100 transition-colors shadow-lg shadow-black/10">
                Return to Analysis
              </button>
            </div>
          </div>

        </div>
      </div>
    </PageTransition>
  );
}
