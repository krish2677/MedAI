import React from 'react';
import { motion } from 'framer-motion';

const scans = [
  { id: 'chest_xray', title: 'Chest X-Ray', desc: 'Pulmonary radiograph — COVID-19, Tuberculosis, Bacterial/Viral Pneumonia & Normal', icon: '🫁', color: 'from-blue-500 to-cyan-400', shadow: 'shadow-blue-500/30', border: 'border-blue-500' },
  { id: 'skin', title: 'Skin Lesion', desc: 'Dermatoscopy — Melanoma, BCC, Actinic Keratosis & 7 conditions', icon: '🔬', color: 'from-teal-500 to-emerald-400', shadow: 'shadow-teal-500/30', border: 'border-teal-500' },
  { id: 'retina', title: 'Retinal Scan', desc: 'Fundus imaging — DR, Glaucoma, Cataract, Retinal Detachment & 10 conditions', icon: '👁️', color: 'from-purple-500 to-indigo-400', shadow: 'shadow-purple-500/30', border: 'border-purple-500' }
];

export default function ScanSelector({ selected, onSelect }) {
  return (
    <div className="w-full flex flex-col gap-5">
      {scans.map((scan) => {
        const isActive = selected === scan.id;
        return (
          <motion.div
            key={scan.id}
            onClick={() => onSelect(scan.id)}
            whileHover={{ scale: 1.02, x: 10 }}
            whileTap={{ scale: 0.98 }}
            className={`cursor-pointer p-6 rounded-2xl border-2 transition-all duration-300 flex items-center gap-6 relative overflow-hidden group ${
              isActive 
                ? `bg-white ${scan.border} ${scan.shadow} shadow-2xl` 
                : 'bg-white/60 border-slate-200 hover:bg-white hover:shadow-lg'
            }`}
          >
            {/* Background decorative glow when active */}
            {isActive && (
              <div className={`absolute -right-10 -top-10 w-32 h-32 bg-gradient-to-br ${scan.color} opacity-10 blur-2xl rounded-full`}></div>
            )}

            {/* Icon Box */}
            <div className={`w-16 h-16 shrink-0 rounded-2xl flex items-center justify-center text-3xl transition-all duration-500 ${
              isActive 
                ? `bg-gradient-to-br ${scan.color} text-white shadow-lg scale-110` 
                : 'bg-slate-100 text-slate-500 opacity-70 group-hover:opacity-100 group-hover:scale-105'
            }`}>
              {scan.icon}
            </div>

            {/* Text */}
            <div className="flex-1 relative z-10">
              <h3 className={`text-xl font-heading font-extrabold mb-1 transition-colors ${isActive ? 'text-slate-800' : 'text-slate-600 group-hover:text-slate-800'}`}>
                {scan.title}
              </h3>
              <p className={`text-sm font-medium transition-colors ${isActive ? 'text-slate-600' : 'text-slate-400 group-hover:text-slate-500'}`}>
                {scan.desc}
              </p>
            </div>

            {/* Selection indicator (Radio Button visual) */}
            <div className={`w-6 h-6 shrink-0 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
              isActive ? `${scan.border} bg-white scale-110` : 'border-slate-300 scale-100'
            }`}>
              {isActive && <div className={`w-2.5 h-2.5 rounded-full bg-gradient-to-br ${scan.color}`}></div>}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
