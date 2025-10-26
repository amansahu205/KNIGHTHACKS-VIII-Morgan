"use client"

import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

interface HeaderProps {
  onNewCase?: () => void
  showNewCaseButton?: boolean
}

export function Header({ onNewCase, showNewCaseButton = false }: HeaderProps) {
  return (
    <header className="relative bg-gradient-to-r from-[#D71920] to-[#8B0000] border-b border-white/20">
      <div className="container mx-auto px-6 py-4 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Image
              src="/morgan-logo.png"
              alt="Morgan & Morgan"
              width={240}
              height={60}
              className="w-auto h-12"
              priority
            />
          </div>

          <h1 className="text-white text-lg md:text-xl font-serif font-bold tracking-wide">
            AI Legal Tender Assistant
          </h1>

          {showNewCaseButton && (
            <Button
              onClick={onNewCase}
              className="bg-[#FFD700] hover:bg-[#FFD700]/90 text-[#8B0000] font-semibold shadow-lg hover:scale-105 transition-transform"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Case
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
