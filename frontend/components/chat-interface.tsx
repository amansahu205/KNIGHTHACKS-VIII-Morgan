"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Bot, User, CheckCircle, XCircle, Edit } from "lucide-react"

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

interface ChatInterfaceProps {
  messages: Message[]
  onMessageAction?: (messageId: string, action: "approve" | "modify" | "reject") => void
}

export function ChatInterface({ messages, onMessageAction }: ChatInterfaceProps) {
  const handleAction = (messageId: string, action: "approve" | "modify" | "reject") => {
    onMessageAction?.(messageId, action)
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
    </div>
  )
}
