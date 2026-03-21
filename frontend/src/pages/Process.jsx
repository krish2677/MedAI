import React from 'react';
import PageTransition from '../components/PageTransition';
import { Microscope, BrainCircuit, Activity, FileText } from 'lucide-react';

export default function Process() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-bg py-16 px-4">
        <div className="max-w-4xl mx-auto space-y-12">
          
          <div className="text-center" data-aos="zoom-in">
            <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-slate-800 mb-4">
              How the AI Works
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Behind the scenes, MedAI uses a sophisticated 4-step pipeline to analyze your symptoms and scans in real time.
            </p>
          </div>

          <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
            
            {/* Step 1 */}
            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active" data-aos="fade-up">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-primary-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                <Microscope size={18} />
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] card p-6 hover:scale-[1.02] transform transition-transform duration-300">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-heading font-bold text-xl text-slate-800">1. Visual Analysis</h3>
                  <span className="text-xs font-bold text-primary-500 bg-primary-50 px-2 py-1 rounded-full">Vision CNN</span>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">
                  The uploaded medical scan (Chest X-Ray, Skin Lesion, or Retinal Scan) is processed through a state-of-the-art highly optimized EfficientNet-B4 Convolutional Neural Network. It extracts thousands of visual features to estimate probabilities for specific conditions.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active" data-aos="fade-up" data-aos-delay="100">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-teal-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                <Activity size={18} />
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] card p-6 hover:scale-[1.02] transform transition-transform duration-300">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-heading font-bold text-xl text-slate-800">2. Symptom Mapping</h3>
                  <span className="text-xs font-bold text-teal-600 bg-teal-50 px-2 py-1 rounded-full">NLP BioBERT</span>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">
                  The textual symptoms you describe are passed through a Clinical BioBERT NLP pipeline. It extracts key medical entities, mapping everyday language to precise ICD-10 medical symptom taxonomies.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active" data-aos="fade-up" data-aos-delay="200">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-blue-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                <BrainCircuit size={18} />
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] card p-6 hover:scale-[1.02] transform transition-transform duration-300">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-heading font-bold text-xl text-slate-800">3. Multimodal Fusion</h3>
                  <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-full">Ensemble</span>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">
                  The visual probabilities and textual symptom weights are combined using an advanced fusion algorithm. This mitigates errors where a scan might look ambiguous but symptoms strongly point to a specific finding.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active" data-aos="fade-up" data-aos-delay="300">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-purple-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                <FileText size={18} />
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] card p-6 hover:scale-[1.02] transform transition-transform duration-300">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-heading font-bold text-xl text-slate-800">4. Report Generation</h3>
                  <span className="text-xs font-bold text-purple-600 bg-purple-50 px-2 py-1 rounded-full">Llama 3 RAG</span>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Using Retrieval-Augmented Generation (RAG), the highest confidence scores trigger a search in our medical vector database. A Lightning-fast Llama-3 model running on Groq synthesizes this context into an easy-to-read, empathetic report.
                </p>
              </div>
            </div>
            
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
