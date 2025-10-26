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
    setIsLoading(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      
      // Use your verified phone number
      const clientPhone = "+12404984206"
      const caseId = metadata?.case_number?.value || "TOOLBAR-CALL"
      const clientName = metadata?.client_name?.value || "Client"

      const requestBody = {
        to_number: String(clientPhone),
        case_id: String(caseId),
        client_name: String(clientName)
      }

      const response = await fetch(`${apiUrl}/api/calls/initiate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || `API error: ${response.status}`)
      }

      if (data.status === "success") {
        toast({
          title: "Call Initiated Successfully!",
          description: `Calling ${clientPhone}... Call SID: ${data.call_sid}`,
        })
      } else if (data.status === "mock") {
        toast({
          title: "Call Initiated (Mock Mode)",
          description: "Configure Twilio credentials for real calls",
        })
      } else {
        throw new Error(data.message || "Unknown error")
      }
    } catch (error) {
      console.error("Call error:", error)
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

  const handleScheduleMeeting = async () => {
    setIsLoading(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      
      // Use hardcoded values for demo (metadata extraction has issues)
      const clientName = "Emily Watson"
      const caseId = "2024-PI-8888"
      
      // Schedule meeting for tomorrow at 2 PM
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      const preferredDate = tomorrow.toISOString().split('T')[0]
      const preferredTime = "14:00"

      const requestBody = {
        client_name: clientName,
        case_id: caseId,
        duration_minutes: 30,
        preferred_date: preferredDate,
        preferred_time: preferredTime
      }

      console.log("Scheduling meeting with:", requestBody)

      const response = await fetch(`${apiUrl}/api/calendar/schedule`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      const data = await response.json()
      
      console.log("API Response:", data)
      console.log("Response status:", response.status)
      console.log("Data status:", data.status)

      if (!response.ok) {
        console.error("Schedule meeting error response:", data)
        const errorMsg = data.detail ? JSON.stringify(data.detail, null, 2) : data.message || data.error || response.statusText
        throw new Error(`API error: ${response.status} - ${errorMsg}`)
      }

      console.log("About to show toast for status:", data.status)

      if (data.status === "mock" || data.status === "mock_created") {
        console.log("Showing mock toast")
        toast({
          title: "Meeting Scheduled (Mock Mode)",
          description: `Meeting with ${clientName} scheduled for tomorrow at 2:00 PM`,
        })
      } else if (data.status === "created") {
        console.log("Showing created toast")
        toast({
          title: "Meeting Scheduled Successfully!",
          description: `Meeting with ${clientName} added to Google Calendar`,
        })
      } else {
        console.log("Unknown status, throwing error")
        throw new Error(data.message || "Unknown error")
      }
    } catch (error) {
      console.error("Schedule meeting error:", error)
      toast({
        title: "Scheduling Failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
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
          className="bg-[#8B1F1F] hover:bg-[#5A1414] text-white shadow-glow hover:scale-105 transition-transform font-sans"
        >
          <Phone className="w-4 h-4 mr-2" />
          Call Client
        </Button>
        <Button
          onClick={handleSendEmail}
          className="bg-[#D4AF37] hover:bg-[#B8941F] text-[#2B1515] shadow-glow hover:scale-105 transition-transform font-sans"
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
