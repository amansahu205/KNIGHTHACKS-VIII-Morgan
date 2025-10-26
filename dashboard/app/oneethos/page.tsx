"use client"

import { useEffect } from "react"
import { Loader2 } from "lucide-react"

export default function OneEthosPage() {
  useEffect(() => {
    // Redirect to the deployed OneEthos app
    window.location.href = "https://ae7271a9-bcdc-4d29-89d5-a3f862014404-26112.lovable.app"
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-cyan-500 to-blue-400">
      <div className="text-center">
        <Loader2 className="w-16 h-16 animate-spin text-white mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Launching OneEthos</h2>
        <p className="text-blue-100">AI for Financial Empowerment</p>
      </div>
    </div>
  )
}
