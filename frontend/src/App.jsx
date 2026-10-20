import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import AOS from 'aos'
import 'aos/dist/aos.css'

import Home from './pages/Home'
import Results from './pages/Results'
import About from './pages/About'
import Process from './pages/Process'
import ModelMetrics from './pages/ModelMetrics'
import Navbar from './components/Navbar'
import { useAnalysis } from './hooks/useAnalysis'

function AnimatedRoutes({ analyze, loading, reportLoading, error, result }) {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home onAnalyze={analyze} loading={loading} />} />
        <Route path="/metrics" element={<ModelMetrics />} />
        <Route path="/about" element={<About />} />
        <Route path="/process" element={<Process />} />
        <Route path="/results" element={
          <Results 
            result={result} 
            error={error} 
            loading={loading}
            reportLoading={reportLoading}
          />
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  const { analyze, loading, reportLoading, error, result } = useAnalysis()

  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      easing: 'ease-out-cubic'
    });
  }, []);

  return (
    <Router>
      <div className="font-body text-slate-800 antialiased selection:bg-primary-200 selection:text-primary-900 min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 relative">
          <AnimatedRoutes 
            analyze={analyze} 
            loading={loading} 
            reportLoading={reportLoading} 
            error={error} 
            result={result} 
          />
        </main>
      </div>
    </Router>
  )
}
