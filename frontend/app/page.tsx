"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { FileUpload } from "@/components/file-upload"
import { ChatInterface } from "@/components/chat-interface"
import { CaseSummaryPanel } from "@/components/case-summary-panel"
import { ActionToolbar } from "@/components/action-toolbar"
import { ModifyModal } from "@/components/modify-modal"
import type { ProcessFileResponse, ContextMetadata } from "@/lib/types"

interface Message {
  id: string
  role: "AI" | "Attorney" | "System"
  content: string
  timestamp: Date
  agentName?: string
  confidence?: number
  requiresApproval?: boolean
  status?: "pending" | "approved" | "rejected" | "modified"
}

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [metadata, setMetadata] = useState<ContextMetadata | null>(null)
  const [attorneyBrief, setAttorneyBrief] = useState<string | null>(null)
  const [agentOutputs, setAgentOutputs] = useState<any[]>([])
  const [modifyingMessageId, setModifyingMessageId] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file)
    setIsProcessing(true)
    setMessages([])
    setMetadata(null)
    setAttorneyBrief(null)
    setAgentOutputs([])

    setMessages([
      {
        id: "init",
        role: "AI",
        content: "Analyzing case file...",
        timestamp: new Date(),
      },
    ])

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch(`${apiUrl}/process_file`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data: ProcessFileResponse = await response.json()

      if (data.attorney_brief) {
        setAttorneyBrief(data.attorney_brief)
        setMessages((prev) => [
          ...prev,
          {
            id: "brief",
            role: "AI",
            content: data.attorney_brief,
            timestamp: new Date(),
            agentName: "Attorney Brief",
            requiresApproval: false,
          },
        ])
      }

      if (data.context_metadata) {
        setMetadata(data.context_metadata)
      }

      if (data.agent_outputs) {
        const agentOutputsArray = Object.entries(data.agent_outputs).map(([name, output]) => ({
          ...output,
          agent_name: name
        }))
        setAgentOutputs(agentOutputsArray)

        const agentMessages: Message[] = agentOutputsArray
          .filter(output => output.status === 'success')
          .map((output, index) => ({
            id: `agent-${index}`,
            role: "AI" as const,
            content: output.recommended_action || output.reasoning_summary || output.message_draft || 'Agent completed successfully',
            timestamp: new Date(),
            agentName: output.agent_name,
            confidence: output.confidence_score,
            requiresApproval: true,
            status: "pending" as const,
            // Enhanced Communication Guru fields
            sentimentScore: output.sentiment_score,
            emotionDetected: output.emotion_detected,
            urgencyLevel: output.urgency_level,
            recommendedMethod: output.recommended_method,
            callRecommendation: output.call_recommendation,
            triggerKeywords: output.trigger_keywords,
          }))

        setMessages((prev) => [...prev, ...agentMessages])
      }

      // Add recommended actions as messages
      if (data.recommended_actions && data.recommended_actions.length > 0) {
        const actionMessage: Message = {
          id: 'actions',
          role: 'System',
          content: `Recommended Actions:\n${data.recommended_actions.slice(0, 5).map((action, i) => `${i + 1}. ${action}`).join('\n')}`,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, actionMessage])
      }
    } catch (error) {
      console.error("[v0] Upload error:", error)
      setMessages((prev) => [
        ...prev,
        {
          id: "error",
          role: "System",
          content: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
          timestamp: new Date(),
        },
      ])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleMessageAction = (messageId: string, action: "approve" | "modify" | "reject") => {
    if (action === "modify") {
      setModifyingMessageId(messageId)
    } else {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, status: action === "approve" ? "approved" : "rejected" } : msg,
        ),
      )

      // Add system message
      const message = messages.find((m) => m.id === messageId)
      if (message) {
        setMessages((prev) => [
          ...prev,
          {
            id: `${action}-${Date.now()}`,
            role: "System",
            content: `${message.agentName || "Agent"} ${action === "approve" ? "approved" : "rejected"}`,
            timestamp: new Date(),
          },
        ])
      }
    }
  }

  const handleSendMessage = async (message: string) => {
    // Add attorney's message
    const attorneyMessage: Message = {
      id: `attorney-${Date.now()}`,
      role: "Attorney",
      content: message,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, attorneyMessage])

    try {
      // Call backend API with case context
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/chat/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: message,
          case_context: {
            client_name: metadata?.client_name?.value,
            case_type: metadata?.case_type?.value,
            attorney_brief: attorneyBrief,
            agent_outputs: agentOutputs
          }
        })
      })

      const data = await response.json()
      
      // Add AI response
      const aiResponse: Message = {
        id: `ai-${Date.now()}`,
        role: "AI",
        content: data.answer || "I can help you with questions about this case.",
        timestamp: new Date(),
        agentName: data.agent || "Legal Assistant",
      }
      setMessages((prev) => [...prev, aiResponse])
    } catch (error) {
      console.error("Chat error:", error)
      // Fallback response
      const aiResponse: Message = {
        id: `ai-${Date.now()}`,
        role: "AI",
        content: "I'm having trouble connecting right now. Please try again.",
        timestamp: new Date(),
        agentName: "Legal Assistant",
      }
      setMessages((prev) => [...prev, aiResponse])
    }
  }

  const handleModifySubmit = (messageId: string, modifiedContent: string) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, content: modifiedContent, status: "modified" } : msg)),
    )

    setMessages((prev) => [
      ...prev,
      {
        id: `modified-${Date.now()}`,
        role: "Attorney",
        content: modifiedContent,
        timestamp: new Date(),
      },
    ])

    setModifyingMessageId(null)
  }

  const handleNewCase = () => {
    // Reset all state to start fresh
    setUploadedFile(null)
    setIsProcessing(false)
    setMessages([])
    setMetadata(null)
    setAttorneyBrief(null)
    setAgentOutputs([])
    setModifyingMessageId(null)
  }

  return (
    <div className="min-h-screen">
      <Header onNewCase={handleNewCase} showNewCaseButton={!!uploadedFile} />

      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Case Summary */}
        <div className="w-80 border-r border-white/10 overflow-y-auto bg-black/20 backdrop-blur-sm">
          <CaseSummaryPanel metadata={metadata} attorneyBrief={attorneyBrief} agentOutputs={agentOutputs} />
        </div>

        {/* Center Panel - Chat + Upload */}
        <div className="flex-1 flex flex-col">
          {!uploadedFile ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <FileUpload onFileUpload={handleFileUpload} isProcessing={isProcessing} />
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-6">
              <ChatInterface 
                messages={messages} 
                onMessageAction={handleMessageAction} 
                caseMetadata={metadata}
                onSendMessage={handleSendMessage}
              />
            </div>
          )}

          {/* Bottom Toolbar */}
          {uploadedFile && <ActionToolbar metadata={metadata} />}
        </div>
      </div>

      {/* Modify Modal */}
      {modifyingMessageId && (
        <ModifyModal
          messageId={modifyingMessageId}
          originalContent={messages.find((m) => m.id === modifyingMessageId)?.content || ""}
          onSubmit={handleModifySubmit}
          onClose={() => setModifyingMessageId(null)}
        />
      )}
    </div>
  )
}
