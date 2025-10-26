"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Bot, User, CheckCircle, XCircle, Edit, Phone, Mail, AlertTriangle, Clock, Send } from "lucide-react"

interface Message {
  id: string
  role: "AI" | "Attorney" | "System"
  content: string
  timestamp: Date
  agentName?: string
  confidence?: number
  requiresApproval?: boolean
  status?: "pending" | "approved" | "rejected" | "modified"
  // Enhanced Communication Guru fields
  sentimentScore?: number
  emotionDetected?: string
  urgencyLevel?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  recommendedMethod?: "call" | "email" | "both"
  callRecommendation?: {
    should_call: boolean
    urgency: string
    reason: string
    talking_points: string[]
  }
  triggerKeywords?: string[]
}

interface ChatInterfaceProps {
  messages: Message[]
  onMessageAction?: (messageId: string, action: "approve" | "modify" | "reject") => void
  caseMetadata?: any
  onSendMessage?: (message: string) => void
}

export function ChatInterface({ messages, onMessageAction, caseMetadata, onSendMessage }: ChatInterfaceProps) {
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = (messageId: string, action: "approve" | "modify" | "reject") => {
    onMessageAction?.(messageId, action)
  }

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return
    
    setIsLoading(true)
    try {
      if (onSendMessage) {
        await onSendMessage(inputMessage)
      }
      setInputMessage("")
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, x: message.role === "Attorney" ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className={`flex gap-3 ${message.role === "Attorney" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
                message.role === "AI" ? "bg-[#D71920]" : message.role === "System" ? "bg-[#8B0000]" : "bg-[#FFD700]"
              }`}
            >
              {message.role === "AI" ? (
                <Bot className="w-5 h-5 text-white" />
              ) : message.role === "System" ? (
                <Bot className="w-5 h-5 text-[#FFD700]" />
              ) : (
                <User className="w-5 h-5 text-[#8B0000]" />
              )}
            </div>

            <div className={`flex-1 max-w-[75%] ${message.role === "Attorney" ? "text-right" : ""}`}>
              <div
                className={`inline-block rounded-2xl px-5 py-3 shadow-glow ${
                  message.role === "AI"
                    ? "bg-[#FFF8DC] text-gray-900"
                    : message.role === "System"
                      ? "bg-[#8B0000]/20 border-2 border-[#FFD700]/50 text-white backdrop-blur-sm"
                      : "bg-[#FFD700] text-[#8B0000]"
                }`}
              >
                {message.agentName && (
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-gray-300">
                    <span className="font-serif font-bold text-xs uppercase tracking-wider">{message.agentName}</span>
                    {message.confidence !== undefined && (
                      <span className="text-xs bg-[#D71920] text-white px-2 py-0.5 rounded-full font-sans">
                        {Math.round(message.confidence * 100)}%
                      </span>
                    )}
                    {message.urgencyLevel && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-sans font-semibold flex items-center gap-1 ${
                        message.urgencyLevel === "CRITICAL" ? "bg-red-600 text-white" :
                        message.urgencyLevel === "HIGH" ? "bg-orange-500 text-white" :
                        message.urgencyLevel === "MEDIUM" ? "bg-yellow-500 text-gray-900" :
                        "bg-green-500 text-white"
                      }`}>
                        <AlertTriangle className="w-3 h-3" />
                        {message.urgencyLevel}
                      </span>
                    )}
                  </div>
                )}

                {/* Sentiment Score Bar */}
                {message.sentimentScore !== undefined && message.sentimentScore > 50 && (
                  <div className="mb-3 p-2 bg-gray-100 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-gray-700">Client Sentiment</span>
                      <span className="text-xs font-bold text-gray-900">{message.sentimentScore}/100</span>
                    </div>
                    <div className="w-full bg-gray-300 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all ${
                          message.sentimentScore >= 86 ? "bg-red-600" :
                          message.sentimentScore >= 71 ? "bg-orange-500" :
                          message.sentimentScore >= 51 ? "bg-yellow-500" :
                          "bg-green-500"
                        }`}
                        style={{ width: `${message.sentimentScore}%` }}
                      />
                    </div>
                    {message.emotionDetected && (
                      <p className="text-xs text-gray-600 mt-1">
                        😰 {message.emotionDetected.replace(/_/g, " ")}
                      </p>
                    )}
                  </div>
                )}

                {/* Trigger Keywords */}
                {message.triggerKeywords && message.triggerKeywords.length > 0 && (
                  <div className="mb-3 flex flex-wrap gap-1">
                    {message.triggerKeywords.map((keyword, idx) => (
                      <span key={idx} className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}

                <p className="text-sm leading-relaxed font-sans whitespace-pre-line">{message.content}</p>
                <p
                  className={`text-xs mt-2 font-sans ${
                    message.role === "AI" 
                      ? "text-gray-600" 
                      : message.role === "System"
                        ? "text-[#FFD700]/80"
                        : "text-[#8B0000]/70"
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>

              {/* Call Recommendation Section */}
              {message.callRecommendation && message.callRecommendation.should_call && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border-2 border-red-200"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-red-600 rounded-full flex items-center justify-center">
                      <Phone className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-bold text-red-900 text-sm">📞 CALL RECOMMENDED</h4>
                        <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">
                          <Clock className="w-3 h-3 inline mr-1" />
                          {message.callRecommendation.urgency.replace(/_/g, " ")}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{message.callRecommendation.reason}</p>
                      
                      {message.callRecommendation.talking_points && message.callRecommendation.talking_points.length > 0 && (
                        <div className="bg-white p-3 rounded-md border border-red-200">
                          <p className="text-xs font-semibold text-gray-700 mb-2">📋 Talking Points:</p>
                          <ul className="space-y-1">
                            {message.callRecommendation.talking_points.map((point, idx) => (
                              <li key={idx} className="text-xs text-gray-600 flex items-start gap-2">
                                <span className="text-red-600 font-bold">{idx + 1}.</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="mt-3 flex gap-2">
                        <Button
                          size="sm"
                          className="bg-[#8B1F1F] hover:bg-[#5A1414] text-white shadow-lg hover:scale-105 transition-transform"
                          onClick={async () => {
                            try {
                              const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
                              
                              // Extract client info from metadata or use defaults
                              const clientPhone = caseMetadata?.client_phone || "+12404984206"
                              const caseId = caseMetadata?.case_number?.value || "DEMO-CASE"
                              const clientName = caseMetadata?.client_name?.value || "Client"
                              
                              console.log("Initiating call to:", clientPhone, "Case:", caseId, "Name:", clientName)
                              
                              const requestBody = {
                                to_number: String(clientPhone),
                                case_id: String(caseId),
                                client_name: String(clientName)
                              }
                              
                              console.log("Request body:", requestBody)
                              
                              const response = await fetch(`${apiUrl}/api/calls/initiate`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify(requestBody)
                              })
                              
                              const data = await response.json()
                              
                              if (!response.ok) {
                                // Show detailed error from backend
                                const errorMsg = data.detail ? JSON.stringify(data.detail, null, 2) : data.message || response.statusText
                                throw new Error(`HTTP ${response.status}: ${errorMsg}`)
                              }
                              
                              if (data.status === "success") {
                                alert(`✅ Call initiated successfully!\n\nCall SID: ${data.call_sid}\nTo: ${data.to}\nFrom: ${data.from}\n\nYour phone should ring shortly!`)
                              } else if (data.status === "mock") {
                                alert(`✅ Call initiated in MOCK mode!\n\nTo: ${clientPhone}\nCase: ${caseId}\n\n(Configure Twilio credentials in .env for real calls)`)
                              } else {
                                alert(`❌ Error: ${data.message || data.error || "Unknown error"}`)
                              }
                            } catch (error) {
                              console.error("Call initiation error:", error)
                              alert(`❌ Error initiating call:\n\n${error instanceof Error ? error.message : String(error)}\n\nCheck console for details.`)
                            }
                          }}
                        >
                          <Phone className="w-4 h-4 mr-1" />
                          Call Client Now
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-[#8B1F1F]/30 text-[#D4AF37] hover:bg-[#8B1F1F]/10"
                          onClick={() => alert("Scheduling call...")}
                        >
                          <Clock className="w-4 h-4 mr-1" />
                          Schedule Call
                        </Button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Email Alternative */}
              {message.recommendedMethod === "email" && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Mail className="w-4 h-4 text-blue-600" />
                    <span className="text-xs font-semibold text-blue-900">Email Response Recommended</span>
                  </div>
                </motion.div>
              )}

              {message.requiresApproval && message.status === "pending" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-3 flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleAction(message.id, "approve")}
                    className="bg-green-600 hover:bg-green-700 text-white shadow-glow hover:scale-105 transition-transform"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleAction(message.id, "modify")}
                    className="bg-[#FFD700] hover:bg-[#FFD700]/90 text-[#8B0000] shadow-glow hover:scale-105 transition-transform"
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Modify
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleAction(message.id, "reject")}
                    className="bg-red-600 hover:bg-red-700 text-white shadow-glow hover:scale-105 transition-transform"
                  >
                    <XCircle className="w-4 h-4 mr-1" />
                    Reject
                  </Button>
                </motion.div>
              )}

              {message.status && message.status !== "pending" && (
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="mt-2">
                  <span
                    className={`inline-block text-xs px-3 py-1 rounded-full font-sans font-semibold ${
                      message.status === "approved"
                        ? "bg-green-600 text-white"
                        : message.status === "rejected"
                          ? "bg-red-600 text-white"
                          : "bg-[#FFD700] text-[#8B0000]"
                    }`}
                  >
                    {message.status.toUpperCase()}
                  </span>
                </motion.div>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {messages.length === 0 && (
        <div className="text-center py-16 text-white/60">
          <Bot className="w-20 h-20 mx-auto mb-4 opacity-30" />
          <p className="font-sans text-lg">Awaiting case file upload...</p>
        </div>
      )}

      {/* Chat Input */}
      {messages.length > 0 && (
        <div className="sticky bottom-0 pt-4 pb-2 bg-gradient-to-t from-black/80 to-transparent backdrop-blur-sm">
          <div className="flex gap-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about this case..."
              disabled={isLoading}
              className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-[#D4AF37]"
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-[#8B1F1F] hover:bg-[#5A1414] text-white"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
