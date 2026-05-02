import { createContext, useContext, useState, ReactNode } from "react"
import Toast from "../components/Toast"

type ToastType = "success" | "error" | "info"

interface ToastConfig {
  message: string
  type?: ToastType
  duration?: number
  autoClose?: boolean
}

interface ToastContextType {
  showToast: (config: ToastConfig) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastConfig | null>(null)

  function showToast(config: ToastConfig) {
    setToast(config)
  }

  function closeToast() {
    setToast(null)
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          autoClose={toast.autoClose}
          onClose={closeToast}
        />
      )}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within ToastProvider")
  }
  return context
}