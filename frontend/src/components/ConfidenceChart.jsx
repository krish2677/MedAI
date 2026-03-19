import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from 'recharts'

export default function ConfidenceChart({ predictions }) {
  if (!predictions || predictions.length === 0) return null

  // Format data for Recharts
  const data = predictions.map(p => ({
    name: p.condition,
    score: Number((p.final_score * 100).toFixed(1)),
    isHigh: p.final_score > 0.75,
    isModerate: p.final_score > 0.45 && p.final_score <= 0.75
  }))

  // Custom tooltips
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-lg">
          <p className="font-semibold text-slate-800">{data.name}</p>
          <div className="flex items-center gap-2 mt-1">
            <div className={`w-3 h-3 rounded-full ${data.isHigh ? 'bg-danger' : data.isModerate ? 'bg-warning' : 'bg-primary-500'}`} />
            <span className="text-sm font-medium text-slate-600">
              {data.score}% Confidence
            </span>
          </div>
        </div>
      )
    }
    return null
  }

  // Determine bar color based on confidence thresholds
  const getBarColor = (entry) => {
    if (entry.isHigh) return '#E53935' // danger (red)
    if (entry.isModerate) return '#FB8C00' // warning (orange)
    return '#3a74d1' // primary-500 (blue)
  }

  return (
    <div className="w-full h-full min-h-[250px] relative">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
          barSize={24}
        >
          <XAxis 
            type="number" 
            domain={[0, 100]} 
            tickFormatter={v => `${v}%`}
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={{ stroke: '#cbd5e1' }}
            tickLine={{ stroke: '#cbd5e1' }}
          />
          <YAxis 
            type="category" 
            dataKey="name" 
            width={120} 
            tick={{ fill: '#334155', fontSize: 13, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f1f5f9' }} />
          
          {/* Reference lines for thresholds */}
          <ReferenceLine x={45} stroke="#cbd5e1" strokeDasharray="3 3" />
          <ReferenceLine x={75} stroke="#cbd5e1" strokeDasharray="3 3" />
          
          <Bar dataKey="score" radius={[0, 4, 4, 0]} animationDuration={1000}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Legend inside the chart area */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-center gap-6 text-xs text-slate-500 pb-1">
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-primary-500" /> Low (0-45%)
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-warning" /> Mod (46-75%)
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-danger" /> High (76-100%)
        </div>
      </div>
    </div>
  )
}
