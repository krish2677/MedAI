import React, { useState, useEffect, useRef } from 'react'
import { Activity, Mic, MicOff } from 'lucide-react'

export default function SymptomInput({ symptoms, setSymptoms }) {
  const maxLength = 5000
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef(null)

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = false

      recognitionRef.current.onresult = (event) => {
        const last = event.results.length - 1
        const text = event.results[last][0].transcript
        setSymptoms(prev => {
          const newText = prev + (prev.endsWith(' ') || prev.length === 0 ? '' : ' ') + text
          return newText.slice(0, maxLength)
        })
      }

      recognitionRef.current.onerror = (event) => {
        console.error("Speech recognition error:", event.error)
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }
  }, [setSymptoms])

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop()
      setIsRecording(false)
    } else {
      if (!recognitionRef.current) {
        alert("Your browser does not support Voice Recognition. Please try Chrome or Edge.")
        return
      }
      recognitionRef.current.start()
      setIsRecording(true)
    }
  }

  const handleChange = (e) => {
    if (e.target.value.length <= maxLength) {
      setSymptoms(e.target.value)
    }
  }

  return (
    <div className="w-full flex flex-col gap-2 relative">
      <div className="flex items-center justify-between">
        <label htmlFor="symptoms" className="text-sm font-bold text-slate-700 flex items-center gap-2">
          <Activity size={16} className="text-primary-600" />
          Patient Symptoms & History
        </label>
        <span className={`text-xs font-medium ${symptoms.length > maxLength * 0.9 ? 'text-warning' : 'text-slate-400'}`}>
          {symptoms.length} / {maxLength}
        </span>
      </div>
      
      <div className="relative group">
        <textarea
          id="symptoms"
          rows={5}
          value={symptoms}
          onChange={handleChange}
          placeholder="Describe the patient's symptoms... (Or click the microphone icon to speak!)"
          className="input-field pr-12 transition-all duration-300 focus:shadow-glow focus:border-primary-400"
        ></textarea>
        
        <button
          type="button"
          onClick={toggleRecording}
          title={isRecording ? "Stop recording" : "Start voice to text"}
          className={`absolute right-3 top-3 p-2 rounded-full transition-all duration-300 transform ${
            isRecording 
              ? 'bg-red-100 text-red-600 animate-pulse scale-110 shadow-glow' 
              : 'bg-slate-100 text-slate-500 hover:bg-primary-50 hover:text-primary-600 hover:scale-105'
          }`}
        >
          {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
      </div>
      
      <p className="text-xs text-slate-500 font-medium">
        Be as detailed as possible to improve NLP extraction accuracy. <span className="text-primary-600">Voice dictation is supported.</span>
      </p>
    </div>
  )
}
