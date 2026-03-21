import React from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import bodyImage from '../assets/body-model.png';

export default function BodyMap({ selected, onSelect }) {
  const x = useMotionValue(200);
  const y = useMotionValue(200);

  const rotateX = useTransform(y, [0, 600], [10, -10]);
  const rotateY = useTransform(x, [0, 600], [-10, 10]);

  function handleMouse(event) {
    const rect = event.currentTarget.getBoundingClientRect();
    x.set(event.clientX - rect.left);
    y.set(event.clientY - rect.top);
  }

  const handleMouseLeave = () => {
    x.set(200);
    y.set(200);
  };

  const hotspots = [
    { id: 'retina', label: 'Retinal Scan', top: '15%', left: '50%', icon: '👁️' },
    { id: 'chest_xray', label: 'Chest X-Ray', top: '32%', left: '50%', icon: '🫁' },
    { id: 'skin', label: 'Skin Lesion', top: '45%', left: '30%', icon: '🔬' }
  ];

  return (
    <div 
      className="relative w-full h-full min-h-[500px] flex items-center justify-center perspective-[1200px]"
      onMouseMove={handleMouse}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        drag
        dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
        dragElastic={0.1}
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className="relative w-[300px] h-[550px] cursor-grab active:cursor-grabbing hover:scale-105 transition-transform duration-300 flex items-center justify-center"
      >
        {/* Glow behind the body */}
        <div className="absolute inset-0 bg-primary-400 opacity-30 blur-[60px] rounded-full translate-z-[-50px]"></div>

        {/* 3D Generated Medical Silhouette */}
        <img 
          src={bodyImage} 
          alt="3D Futuristic Medical Body" 
          className="w-full h-full object-contain drop-shadow-2xl mix-blend-multiply opacity-90"
          style={{ mixBlendMode: 'darken' }}
          draggable="false"
        />

        {/* Interactive Hotspots */}
        {hotspots.map((spot) => (
          <div
            key={spot.id}
            onClick={() => onSelect(spot.id)}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center cursor-pointer group"
            style={{ 
              top: spot.top, 
              left: spot.left,
              transform: `translateZ(${selected === spot.id ? '60px' : '30px'})`
            }}
          >
            {/* Ping animation ring */}
            {selected === spot.id && (
              <span className="absolute w-12 h-12 rounded-full bg-teal-400 opacity-40 animate-ping"></span>
            )}
            
            {/* Core dot */}
            <div className={`relative z-10 w-6 h-6 rounded-full border-2 transition-all duration-300 shadow-glow flex items-center justify-center ${
              selected === spot.id 
                ? 'bg-teal-400 border-white scale-125' 
                : 'bg-primary-500 border-primary-200 hover:bg-teal-300 hover:scale-110'
            }`}>
              <span className="text-[10px] leading-none text-white font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                 {/* Empty to keep visual clean, use tooltip next */}
              </span>
            </div>

            {/* Tooltip Label */}
            <div className={`absolute left-8 px-3 py-1.5 rounded-lg whitespace-nowrap font-bold text-sm shadow-xl transition-all duration-300 backdrop-blur-md ${
              selected === spot.id
                ? 'bg-teal-500/90 text-white translate-x-0 opacity-100'
                : 'bg-white/80 text-slate-700 -translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100'
            }`}>
              {spot.icon} {spot.label}
            </div>
          </div>
        ))}

        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-slate-400 text-xs font-semibold tracking-widest uppercase" style={{ transform: "translateZ(20px)" }}>
           Interactive 3D Scan Selector
        </div>
      </motion.div>
    </div>
  );
}
