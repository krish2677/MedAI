import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileImage, X } from 'lucide-react'

export default function ImageUpload({ onImageSelected, selectedImage }) {
  const [preview, setPreview] = useState(selectedImage ? URL.createObjectURL(selectedImage) : null)

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles?.length > 0) {
      const file = acceptedFiles[0]
      setPreview(URL.createObjectURL(file))
      onImageSelected(file)
    }
  }, [onImageSelected])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      // DICOM often requires specialty parsers in browser, but we accept it for passing to backend
      'application/dicom': ['.dcm'] 
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  })

  const handleClear = (e) => {
    e.stopPropagation()
    setPreview(null)
    onImageSelected(null)
  }

  return (
    <div className="w-full">
      <div 
        {...getRootProps()} 
        className={`upload-zone relative flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 transition-all duration-200
          ${isDragActive ? 'border-primary-500 bg-primary-50 scale-[1.02]' : 'border-slate-300 hover:border-primary-400 bg-white'}
          ${isDragReject ? 'border-danger bg-red-50' : ''}
          ${preview ? 'p-2' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {preview ? (
          <div className="relative w-full h-64 group rounded-lg overflow-hidden bg-slate-100 flex items-center justify-center">
            <img 
              src={preview} 
              alt="Uploaded scan" 
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <p className="text-white font-medium flex items-center gap-2">
                <UploadCloud size={20} /> Click or drag to replace
              </p>
            </div>
            <button
              onClick={handleClear}
              className="absolute top-2 right-2 p-1.5 bg-black/50 hover:bg-danger text-white rounded-full transition-colors"
              title="Remove image"
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center space-y-4 py-8">
            <div className="p-4 bg-primary-50 rounded-full text-primary-600 mb-2">
              <UploadCloud size={40} strokeWidth={1.5} />
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-800">
                Drag & drop your medical image here
              </p>
              <p className="text-sm text-slate-500 mt-1">
                or click to browse from your device
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
              <span className="flex items-center gap-1"><FileImage size={14}/> JPG</span>
              <span className="flex items-center gap-1"><FileImage size={14}/> PNG</span>
              <span className="flex items-center gap-1"><FileImage size={14}/> DCM</span>
              <span>(Max 10MB)</span>
            </div>
          </div>
        )}
      </div>
      {isDragReject && (
        <p className="text-danger text-sm mt-2 flex items-center gap-1">
          <X size={14} /> File type not supported or exceeds 10MB limit.
        </p>
      )}
    </div>
  )
}
