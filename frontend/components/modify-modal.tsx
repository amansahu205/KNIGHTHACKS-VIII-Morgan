"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { X } from "lucide-react"

interface ModifyModalProps {
  messageId: string
  originalContent: string
  onSubmit: (messageId: string, modifiedContent: string) => void
  onClose: () => void
}

export function ModifyModal({ messageId, originalContent, onSubmit, onClose }: ModifyModalProps) {
  const [content, setContent] = useState(originalContent)

  const handleSubmit = () => {
    if (content.trim()) {
      onSubmit(messageId, content)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="w-full max-w-2xl"
      >
        <Card className="bg-white p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-serif font-bold text-[#D71920]">Modify Agent Output</h3>
            <Button variant="ghost" size="sm" onClick={onClose} className="text-gray-500 hover:text-gray-700">
              <X className="w-5 h-5" />
            </Button>
          </div>

          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full h-48 p-4 border border-gray-300 rounded-lg font-sans text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-[#D71920] resize-none"
            placeholder="Enter your modifications..."
          />

          <div className="flex justify-end gap-3 mt-4">
            <Button variant="outline" onClick={onClose} className="font-sans bg-transparent">
              Cancel
            </Button>
            <Button onClick={handleSubmit} className="bg-[#D71920] hover:bg-[#B01518] text-white shadow-glow font-sans">
              Submit Change
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
