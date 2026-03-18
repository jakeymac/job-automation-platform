import Header from "./Header"
import type { ReactNode } from "react"

interface Props {
  children: ReactNode
}

export default function Layout({ children }: Props) {
  return (
    <div>
      <Header />

      <main style={{ padding: "40px" }}>
        {children}
      </main>
    </div>
  )
}