"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Phone, Mail, Calendar } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { ContextMetadata } from "@/lib/types"

interface ActionToolbarProps {
  metadata: ContextMetadata | null
}

export function ActionToolbar({ metadata }: ActionToolbarProps) {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleCallClient = async () => {
    if (!metadata?.client_name) {
      toast({
        title: "Missing Information",
        description: "Client information not available",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const response = await fetch(`${apiUrl}/call_client`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          client_name: metadata.client_name,
          phone: metadata.phone || "555-0100",
          reason: "Case review follow-up",
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      toast({
        title: "Call Initiated",
        description: data.message || `Calling ${metadata.client_name}...`,
      })
    } catch (error) {
      console.error("[v0] Call error:", error)
      toast({
        title: "Call Failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendEmail = () => {
    toast({
      title: "Email Draft Created",
      description: "Opening email client...",
    })
  }

  const handleScheduleMeeting = () => {
    toast({
      title: "Calendar Opened",
      description: "Select a meeting time...",
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-t border-white/20 bg-black/30 backdrop-blur-sm p-4"
    >
      <div className="flex items-center justify-center gap-4">
        <Button
          onClick={handleCallClient}
          disabled={isLoading}
          className="bg-[#D71920] hover:bg-[#B01518] text-white shadow-glow hover:scale-105 transition-transform font-sans"
        >
          <Phone className="w-4 h-4 mr-2" />
          Call Client
        </Button>
        <Button
          onClick={handleSendEmail}
          className="bg-[#FFD700] hover:bg-[#FFD700]/90 text-[#8B0000] shadow-glow hover:scale-105 transition-transform font-sans"
        >
          <Mail className="w-4 h-4 mr-2" />
          Send Email
        </Button>
        <Button
          onClick={handleScheduleMeeting}
          className="bg-white/20 hover:bg-white/30 text-white border border-white/30 shadow-glow hover:scale-105 transition-transform font-sans"
        >
          <Calendar className="w-4 h-4 mr-2" />
          Schedule Meeting
        </Button>
      </div>
    </motion.div>
  )
}
