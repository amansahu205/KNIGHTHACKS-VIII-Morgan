"use client"

import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import Image from "next/image"

export default function Home() {
  const apps = [
    {
      title: "OneEthos",
      subtitle: "AI for Financial Empowerment",
      description:
        "AI-powered solutions that democratize financial advice, deliver personalized learning, and empower informed decision-making.",
      logo: "/oneethos-logo.png",
      href: "/oneethos",
      theme: "oneethos",
      logoHeight: 40,
    },
    {
      title: "Morgan & Morgan",
      subtitle: "AI Legal Tender",
      description:
        "AI orchestrator that helps legal teams cut through chaos, identify what matters, and act fast with intelligent task routing.",
      logo: "/morgan-logo.png",
      href: "/morgan",
      theme: "morgan",
      logoHeight: 64,
    },
    {
      title: "ServiceNow",
      subtitle: "Knowledge Gap Request Agent",
      description:
        "Intelligent agent that analyzes requests, identifies emerging needs, and recommends new accelerators for your portfolio.",
      logo: "/servicenow-logo.png",
      href: "/servicenow",
      theme: "servicenow",
      logoHeight: 64,
    },
  ]

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#0a0a0a]">
      <div className="absolute inset-0 bg-gradient-to-br from-zinc-950 via-black to-zinc-950" />

      <div className="absolute top-0 -left-40 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-0 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] animate-pulse [animation-delay:2s]" />

      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8">
        <div className="text-center mb-24">
          <div className="relative inline-block mb-6">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-cyan-500 to-blue-400 blur-3xl opacity-30 animate-pulse" />
            <h1 className="relative text-7xl md:text-8xl lg:text-9xl font-black tracking-tighter bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-300 bg-clip-text text-transparent drop-shadow-[0_0_80px_rgba(59,130,246,0.5)] animate-[shimmer_3s_ease-in-out_infinite]">
              Synapse
            </h1>
          </div>

          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            Access your suite of AI-powered applications. Select a plugin to launch the dedicated app.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <Link key={app.title} href={app.href} className="group">
              <Card
                className={`app-card app-card-${app.theme} h-full p-8 transition-all duration-500 hover:scale-[1.02] border-0 relative overflow-hidden`}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-white/[0.07] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative z-10 flex flex-col h-full">
                  <div className="mb-8 group-hover:scale-105 transition-transform duration-300">
                    <Image
                      src={app.logo || "/placeholder.svg"}
                      alt={`${app.title} logo`}
                      width={200}
                      height={app.logoHeight}
                      className="object-contain h-16"
                    />
                  </div>

                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-zinc-300 mb-2">{app.subtitle}</h3>
                    <p className="text-sm text-zinc-500 leading-relaxed mb-8">{app.description}</p>
                  </div>

                  <Button className={`w-full app-button-${app.theme} group/btn transition-all duration-300`}>
                    Launch App
                    <ArrowRight className="ml-2 w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                  </Button>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
