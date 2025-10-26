import type React from "react"
import type { Metadata } from "next"
import { Merriweather, Poppins } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { Toaster } from "@/components/ui/toaster"
import "./globals.css"

const merriweather = Merriweather({
  subsets: ["latin"],
  weight: ["300", "400", "700", "900"],
  variable: "--font-merriweather",
})
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-poppins",
})

export const metadata: Metadata = {
  title: "Morgan & Morgan AI Attorney Portal",
  description: "For The People™ — AI Legal Tender Assistant",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body 
        className={`${merriweather.variable} ${poppins.variable} font-sans antialiased`}
        suppressHydrationWarning
      >
        {children}
        <Toaster />
        <Analytics />
      </body>
    </html>
  )
}
