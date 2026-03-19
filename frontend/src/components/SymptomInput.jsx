import React from 'react'
import { Activity } from 'lucide-react'

export default function SymptomInput({ symptoms, setSymptoms }) {
  const maxLength = 5000

  const handleChange = (e) => {
    if (e.target.value.length <= maxLength) {
      setSymptoms(e.target.value)
    }
  }

  return (
    <div className="w-full flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <label htmlFor="symptoms" className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          <Activity size={16} className="text-primary-600" />
          Patient Symptoms & History
        </label>
        <span className={`text-xs ${symptoms.length > maxLength * 0.9 ? 'text-warning' : 'text-slate-400'}`}>
          {symptoms.length} / {maxLength}
        </span>
      </div>
      
      <textarea
        id="symptoms"
        rows={5}
        value={symptoms}
        onChange={handleChange}
        placeholder="Describe the patient's symptoms, duration, severity, and any relevant medical history... (e.g., 'Patient presents with sharp chest pain for 2 days, accompanied by dry cough and shortness of breath. No fever.')"
        className="input-field"
      ></textarea>
      
      <p className="text-xs text-slate-500">
        Be as detailed as possible to improve NLP extraction accuracy. Include duration, severity, and related conditions.
      </p>
    </div>
  )
}
