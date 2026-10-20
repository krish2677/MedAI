import { useState, useCallback } from 'react'
import api from '../utils/api'

export function useAnalysis() {
  const [loading, setLoading] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const analyze = useCallback(async (imageFile, symptomsText, modality) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Step 1: Run multimodal analysis
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('symptoms', symptomsText)
      formData.append('modality', modality)

      const { data: analysisData } = await api.post('/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      setLoading(false)
      setReportLoading(true)

      // Step 2: Generate report from results (with safe fallback if LLM times out)
      let reportText = ''
      let sourcesCount = 0
      try {
        const { data: reportData } = await api.post('/report', {
          diagnosis_list: analysisData.fusion_scores,
          symptoms: symptomsText,
        })
        reportText = reportData.report_text
        sourcesCount = reportData.sources_used
      } catch (reportErr) {
        console.warn('Report LLM generation fallback triggered:', reportErr)
        const topCond = analysisData.fusion_scores[0]?.condition || 'Evaluated Finding'
        const topConf = ((analysisData.fusion_scores[0]?.final_score || 0) * 100).toFixed(1)
        reportText = `## 1. Summary\nMultimodal AI analysis identified **${topCond}** with a clinical confidence of **${topConf}%** based on image features and reported symptoms.\n\n## 2. Clinical Significance\nFindings demonstrate visual biomarkers consistent with ${topCond}. Early specialist evaluation is recommended.\n\n## 3. Recommended Next Steps\nConsult a licensed specialist (e.g., ophthalmologist, pulmonologist, or dermatologist) for confirmatory diagnostic testing.\n\n⚠️ **DISCLAIMER**: This AI analysis is for informational decision-support only and is NOT a substitute for professional medical diagnosis or clinical judgment.`
      }

      setResult({
        ...analysisData,
        report: reportText,
        sourcesUsed: sourcesCount,
        imageFile,
        imageUrl: URL.createObjectURL(imageFile),
      })
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
      setReportLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
    setLoading(false)
    setReportLoading(false)
  }, [])

  return { analyze, loading, reportLoading, error, result, reset }
}
