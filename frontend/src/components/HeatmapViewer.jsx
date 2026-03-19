import React, { useState } from 'react'
import { Layers, Scan, Download } from 'lucide-react'

export default function HeatmapViewer({ originalSrc, heatmapBase64 }) {
  const [showHeatmap, setShowHeatmap] = useState(false)
  
  const heatmapSrc = heatmapBase64 
    ? `data:image/png;base64,${heatmapBase64}` 
    : originalSrc

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = showHeatmap ? heatmapSrc : originalSrc
    link.download = showHeatmap ? 'gradcam-heatmap.png' : 'original-scan.png'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Toggle Controls */}
      <div className="flex items-center justify-between p-1 bg-slate-100 rounded-lg w-full max-w-sm mx-auto">
        <button
          onClick={() => setShowHeatmap(false)}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition-all
            ${!showHeatmap ? 'bg-white shadow-sm text-primary-900' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <Scan size={16} />
          Original Scan
        </button>
        <button
          onClick={() => setShowHeatmap(true)}
          disabled={!heatmapBase64}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition-all
            ${showHeatmap ? 'bg-primary-900 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'}
            ${!heatmapBase64 ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Layers size={16} />
          AI Heatmap
        </button>
      </div>

      {/* Image Viewer */}
      <div className="relative w-full aspect-square md:aspect-[4/3] bg-black rounded-xl overflow-hidden shadow-inner group">
        <img
          src={showHeatmap ? heatmapSrc : originalSrc}
          alt={showHeatmap ? "Grad-CAM AI Focus Map" : "Original Medical Scan"}
          className="w-full h-full object-contain transition-opacity duration-300"
        />
        
        {/* Overlay Badges */}
        <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full font-medium tracking-wide">
          {showHeatmap ? 'Grad-CAM Overlay' : 'Input Image'}
        </div>
        
        <button 
          onClick={handleDownload}
          className="absolute bottom-4 right-4 bg-white/20 hover:bg-white/40 backdrop-blur-md text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-all shadow-xl"
          title="Download Image"
        >
          <Download size={18} />
        </button>
      </div>

      {/* Caption */}
      <div className="text-center min-h-[40px]">
        {showHeatmap ? (
          <p className="text-sm text-slate-600 animate-fade-in flex items-center justify-center gap-2">
            <span className="w-3 h-3 rounded-full bg-gradient-to-r from-red-500 via-orange-400 to-yellow-300 shadow-sm block"></span>
            Warm regions (red/orange) indicate where the AI focused its attention
          </p>
        ) : (
          <p className="text-sm text-slate-500 animate-fade-in">
            Original unprocessed medical image
          </p>
        )}
      </div>
    </div>
  )
}
