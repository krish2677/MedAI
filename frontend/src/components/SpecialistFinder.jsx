import React from 'react';
import { MapPin, ExternalLink } from 'lucide-react';

export default function SpecialistFinder({ scores }) {
  if (!scores || scores.length === 0) return null;
  
  const topCondition = scores[0].condition.toLowerCase();
  let specialist = 'General Practitioner';
  let searchTerm = 'Doctor';

  // Naive specialist mapping based on condition keywords
  if (topCondition.includes('melanoma') || topCondition.includes('nevus') || topCondition.includes('keratosis') || topCondition.includes('carcinoma') || topCondition.includes('skin')) {
    specialist = 'Dermatologist';
    searchTerm = 'Dermatologist';
  } else if (topCondition.includes('pneumonia') || topCondition.includes('covid') || topCondition.includes('tuberculosis') || topCondition.includes('lung') || topCondition.includes('opacity') || topCondition.includes('chest')) {
    specialist = 'Pulmonologist';
    searchTerm = 'Pulmonologist';
  } else if (topCondition.includes('retinopathy') || topCondition.includes('glaucoma') || topCondition.includes('cataract') || topCondition.includes('macular') || topCondition.includes('eye')) {
    specialist = 'Ophthalmologist';
    searchTerm = 'Ophthalmologist';
  }

  const handleSearch = () => {
    const query = encodeURIComponent(`${searchTerm} near me`);
    window.open(`https://www.google.com/maps/search/${query}`, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="card p-5 bg-gradient-to-br from-primary-50 to-white border border-primary-200 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 relative overflow-hidden group">
      {/* Decorative background element */}
      <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary-100 rounded-full opacity-50 blur-xl group-hover:scale-150 transition-transform duration-700"></div>
      
      <div className="relative z-10 flex items-start gap-4">
        <div className="shrink-0 w-12 h-12 rounded-full bg-white text-primary-600 flex items-center justify-center shadow-sm border border-primary-100">
          <MapPin size={24} className="animate-bounce" style={{ animationDuration: '2s' }} />
        </div>
        <div className="flex-1">
          <h3 className="font-heading font-extrabold text-slate-800 text-lg mb-1">Find a Specialist</h3>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
            Based on your AI results, we recommend consulting a certified <strong className="text-primary-800">{specialist}</strong> for a formal clinical diagnosis.
          </p>
          <button 
            onClick={handleSearch}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 hover:shadow-glow transition-all active:scale-95"
          >
            Search on Google Maps <ExternalLink size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
