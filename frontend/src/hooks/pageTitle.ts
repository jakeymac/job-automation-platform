import { useEffect } from "react"

export function pageTitle(title: string) {
  useEffect(() => {
    document.title = `${title}`
  }, [title])
}