"use client"

import { useEffect } from "react"
import { Loader2 } from "lucide-react"

export default function MorganPage() {
  useEffect(() => {
    // Redirect to the deployed Morgan & Morgan app
    window.location.href = "https://v0-knight-hacks.vercel.app"
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#8B1F1F] via-[#5A1414] to-black">
      <div className="text-center">
        <Loader2 className="w-16 h-16 animate-spin text-[#D4AF37] mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Launching Morgan & Morgan AI Legal Assistant</h2>
        <p className="text-[#D4AF37]">Redirecting to application...</p>
      </div>
    </div>
  )
}
