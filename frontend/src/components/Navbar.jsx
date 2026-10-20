import React from 'react';
import { NavLink } from 'react-router-dom';
import { Stethoscope, Info, ActivitySquare, BarChart3 } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm" data-aos="fade-down" data-aos-duration="600">
      <div className="max-w-[1400px] mx-auto px-4 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2 transition-transform hover:scale-105">
          <Stethoscope size={24} className="text-primary-500 animate-pulse" />
          <span className="font-heading font-extrabold text-xl tracking-tight text-slate-800">
            Med<span className="text-primary-500">AI</span>
          </span>
        </NavLink>
        
        <div className="flex items-center gap-6">
          <NavLink 
            to="/" 
            className={({isActive}) => `text-sm font-bold flex items-center gap-1.5 transition-all hover:-translate-y-0.5 ${isActive ? 'text-primary-600' : 'text-slate-500 hover:text-primary-500'}`}
          >
            Home
          </NavLink>
          <NavLink 
            to="/metrics" 
            className={({isActive}) => `text-sm font-bold flex items-center gap-1.5 transition-all hover:-translate-y-0.5 ${isActive ? 'text-primary-600' : 'text-slate-500 hover:text-primary-500'}`}
          >
            <BarChart3 size={16} /> Model Analytics
          </NavLink>
          <NavLink 
            to="/process" 
            className={({isActive}) => `text-sm font-bold flex items-center gap-1.5 transition-all hover:-translate-y-0.5 ${isActive ? 'text-primary-600' : 'text-slate-500 hover:text-primary-500'}`}
          >
            <ActivitySquare size={16} /> Process
          </NavLink>
          <NavLink 
            to="/about" 
            className={({isActive}) => `text-sm font-bold flex items-center gap-1.5 transition-all hover:-translate-y-0.5 ${isActive ? 'text-primary-600' : 'text-slate-500 hover:text-primary-500'}`}
          >
            <Info size={16} /> About
          </NavLink>
        </div>
      </div>
    </nav>
  );
}
