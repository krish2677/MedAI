import React from 'react'
import { AlertCircle, ShieldAlert, CheckCircle2 } from 'lucide-react'

export default function UrgencyBadge({ level }) {
  if (!level) return null

  switch (level.toUpperCase()) {
    case 'HIGH':
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-50 text-red-700 border border-red-200">
          <ShieldAlert size={16} className="animate-pulse" />
          <span className="text-sm font-bold uppercase tracking-wider">High Urgency</span>
        </div>
      )
    case 'MODERATE':
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-50 text-orange-700 border border-orange-200">
          <AlertCircle size={16} />
          <span className="text-sm font-bold uppercase tracking-wider">Moderate Urgency</span>
        </div>
      )
    case 'LOW':
    default:
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-200">
          <CheckCircle2 size={16} />
          <span className="text-sm font-bold uppercase tracking-wider">Routine Follow-up</span>
        </div>
      )
  }
}
