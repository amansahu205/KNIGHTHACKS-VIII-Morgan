"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Upload, FileText, AlertCircle, CheckCircle } from "lucide-react"
import { useState, useCallback } from "react"
import { Card } from "@/components/ui/card"

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>
  isProcessing: boolean
}

export function FileUpload({ onFileUpload, isProcessing }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [uploadComplete, setUploadComplete] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith(".txt")) {
      setError(null)
      handleUpload(file)
    } else {
      setError("Please upload a .txt file")
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setError(null)
      handleUpload(file)
    }
  }, [])

  const handleUpload = async (file: File) => {
    setUploadProgress(0)
    setError(null)
    setUploadComplete(false)

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 10, 90))
    }, 100)

    try {
      await onFileUpload(file)
      setUploadProgress(100)
      setUploadComplete(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
      console.error("[v0] Upload error:", err)
    } finally {
      clearInterval(progressInterval)
    }
  }

  return (
    <Card className="p-12 border-2 border-dashed border-white/30 hover:border-[#FFD700] transition-colors bg-white/5 backdrop-blur-sm">
      <motion.div
        animate={isDragging ? { scale: 1.02 } : { scale: 1 }}
        transition={{ duration: 0.2 }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative ${isDragging ? "ring-4 ring-[#FFD700]/40 rounded-lg" : ""}`}
      >
        <div className="text-center">
          <motion.div
            animate={isDragging ? { y: -10 } : { y: 0 }}
            className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-[#FFD700]/20 mb-6 shadow-glow"
          >
            {isProcessing ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              >
                <FileText className="w-12 h-12 text-[#FFD700]" />
              </motion.div>
            ) : uploadComplete ? (
              <CheckCircle className="w-12 h-12 text-green-400" />
            ) : (
              <Upload className="w-12 h-12 text-[#FFD700]" />
            )}
          </motion.div>

          <h3 className="text-2xl font-serif font-bold text-white mb-3">
            {isProcessing ? "Processing Case File..." : uploadComplete ? "Upload Complete" : "Upload Case File"}
          </h3>

          <p className="text-white/70 mb-8 font-sans text-sm">Drag and drop your .txt file here, or click to browse</p>

          <input
            type="file"
            accept=".txt"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            disabled={isProcessing}
          />

          <label htmlFor="file-upload">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-block bg-[#D71920] text-white px-10 py-4 rounded-lg font-sans font-semibold uppercase tracking-wider cursor-pointer hover:bg-[#B01518] transition-colors shadow-glow"
            >
              Select File
            </motion.div>
          </label>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 bg-red-900/50 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-200 backdrop-blur-sm"
            >
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm font-sans">{error}</span>
            </motion.div>
          )}

          {uploadProgress > 0 && uploadProgress < 100 && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
              <div className="w-full bg-white/20 rounded-full h-4 overflow-hidden backdrop-blur-sm">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  className="h-full bg-gradient-to-r from-[#D71920] to-[#FFD700] shadow-glow"
                />
              </div>
              <p className="text-sm text-white/80 mt-3 font-sans">{uploadProgress}% uploaded</p>
            </motion.div>
          )}
        </div>
      </motion.div>
    </Card>
  )
}
