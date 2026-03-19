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

      // Step 2: Generate report from results
      const { data: reportData } = await api.post('/report', {
        diagnosis_list: analysisData.fusion_scores,
        symptoms: symptomsText,
      })

      setResult({
        ...analysisData,
        report: reportData.report_text,
        sourcesUsed: reportData.sources_used,
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
