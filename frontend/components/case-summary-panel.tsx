"use client"

import { motion } from "framer-motion"
import { Scale, FileText, CheckCircle2, AlertCircle } from "lucide-react"
import { Card } from "@/components/ui/card"
import type { ContextMetadata } from "@/lib/types"

interface CaseSummaryPanelProps {
  metadata: ContextMetadata | null
  attorneyBrief: string | null
  agentOutputs: any[]
}

export function CaseSummaryPanel({ metadata, attorneyBrief, agentOutputs }: CaseSummaryPanelProps) {
  if (!metadata && !attorneyBrief) {
    return (
      <div className="p-6 text-center text-white/60">
        <Scale className="w-12 h-12 mx-auto mb-3 opacity-40" />
        <p className="text-sm font-sans">Upload a case file to begin</p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h2 className="text-[#FFD700] font-serif font-bold text-xl mb-4 flex items-center gap-2">
          <Scale className="w-5 h-5" />
          Case Details
        </h2>

        {metadata && (
          <Card className="bg-white/10 backdrop-blur-sm border-white/20 p-4 space-y-3">
            {metadata.case_number?.value && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Case Number</p>
                <p className="text-white font-sans font-medium">{metadata.case_number.value}</p>
              </div>
            )}
            {metadata.client_name?.value && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Client</p>
                <p className="text-white font-sans font-medium">{metadata.client_name.value}</p>
              </div>
            )}
            {metadata.case_type?.value && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Type</p>
                <p className="text-white font-sans font-medium capitalize">{metadata.case_type.value}</p>
              </div>
            )}
            {metadata.insurance_company?.value && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Insurance</p>
                <p className="text-white font-sans font-medium">{metadata.insurance_company.value}</p>
              </div>
            )}
            {metadata.date_of_incident?.value && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Incident Date</p>
                <p className="text-white font-sans font-medium">{metadata.date_of_incident.value}</p>
              </div>
            )}
            {metadata.medical_providers && metadata.medical_providers.length > 0 && (
              <div>
                <p className="text-white/60 text-xs font-sans uppercase tracking-wide">Medical Providers</p>
                <div className="space-y-1 mt-1">
                  {metadata.medical_providers.slice(0, 3).map((provider, idx) => (
                    <p key={idx} className="text-white font-sans text-sm">{provider.value}</p>
                  ))}
                  {metadata.medical_providers.length > 3 && (
                    <p className="text-white/60 text-xs font-sans">+{metadata.medical_providers.length - 3} more</p>
                  )}
                </div>
              </div>
            )}
          </Card>
        )}
      </motion.div>

      {attorneyBrief && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h2 className="text-[#FFD700] font-serif font-bold text-xl mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Attorney Brief
          </h2>
          <Card className="bg-white/10 backdrop-blur-sm border-white/20 p-4">
            <p className="text-white/90 text-sm font-sans leading-relaxed">{attorneyBrief}</p>
          </Card>
        </motion.div>
      )}

      {agentOutputs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <h2 className="text-[#FFD700] font-serif font-bold text-xl mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            Agent Findings
          </h2>
          <div className="space-y-3">
            {agentOutputs.map((output, index) => (
              <Card
                key={index}
                className="bg-white/10 backdrop-blur-sm border-white/20 p-4 hover:bg-white/15 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <p className="text-white font-sans font-semibold text-sm">{output.agent_name}</p>
                  <div className="flex items-center gap-1">
                    {output.confidence >= 0.8 ? (
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-yellow-400" />
                    )}
                    <span className="text-white/80 text-xs font-sans">{Math.round(output.confidence * 100)}%</span>
                  </div>
                </div>
                <p className="text-white/70 text-xs font-sans leading-relaxed">{output.summary}</p>
              </Card>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
