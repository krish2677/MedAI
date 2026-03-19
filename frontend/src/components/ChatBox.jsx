import React, { useState, useRef, useEffect } from 'react'
import { Send, User, Stethoscope, Loader2 } from 'lucide-react'
import api from '../utils/api'

export default function ChatBox({ diagnosisContext }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "I'm your AI Medical Assistant. Do you have any follow-up questions about your diagnostic report?"
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const response = await api.post('/chat', {
        message: userMsg,
        conversation_history: messages.slice(1), // Exclude initial greeting
        diagnosis_context: diagnosisContext
      })
      
      setMessages(response.data.updated_history.length > 0 
        ? [{ role: 'assistant', content: "I'm your AI Medical Assistant. Do you have any follow-up questions about your diagnostic report?" }, ...response.data.updated_history]
        : [...messages, { role: 'user', content: userMsg }, { role: 'assistant', content: response.data.response }]
      )
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm sorry, I'm having trouble connecting right now. Please consult your physician for answers to your questions." 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card h-[500px] flex flex-col overflow-hidden border border-slate-200">
      <div className="bg-primary-900 text-white p-4 shrink-0 flex items-center justify-between">
        <h3 className="font-heading font-semibold flex items-center gap-2">
          <Stethoscope size={18} className="text-teal-400" />
          Follow-up Questions
        </h3>
        <span className="text-xs bg-white/20 px-2 py-1 rounded-full backdrop-blur-sm shadow-sm">
          AI Assistant
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center
              ${msg.role === 'user' ? 'bg-primary-100 text-primary-700' : 'bg-teal-500 text-white'}`}
            >
              {msg.role === 'user' ? <User size={16} /> : <Stethoscope size={16} />}
            </div>
            
            <div className={`p-3 rounded-2xl text-sm ${
              msg.role === 'user' 
                ? 'bg-primary-600 text-white rounded-tr-none' 
                : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none shadow-sm'
            }`}>
              {msg.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < msg.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="shrink-0 w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center">
              <Stethoscope size={16} />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-white border border-slate-200 shadow-sm flex items-center gap-2 text-slate-500">
              <Loader2 size={16} className="animate-spin text-primary-500" />
              <span className="text-sm">Analyzing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-100 shrink-0">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your diagnosis, next steps, or what terms mean..."
            className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-400 focus:bg-white transition-all text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-1.5 p-2 rounded-full bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50 disabled:hover:bg-primary-600 transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  )
}
