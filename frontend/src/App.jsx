import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import Results from './pages/Results'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  const { analyze, loading, reportLoading, error, result } = useAnalysis()

  return (
    <Router>
      <div className="font-body text-slate-800 antialiased selection:bg-primary-200 selection:text-primary-900">
        <Routes>
          <Route 
            path="/" 
            element={<Home onAnalyze={analyze} loading={loading} />} 
          />
          <Route 
            path="/results" 
            element={
              <Results 
                result={result} 
                error={error} 
                loading={loading}
                reportLoading={reportLoading}
              />
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}
