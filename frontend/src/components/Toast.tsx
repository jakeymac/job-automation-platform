import { useEffect, useState } from "react"

interface ToastProps {
    message: string
    type? : "success" | "error" | "info"
    duration?: number
    autoClose?: boolean
    onClose: () => void
}

export default function Toast({
    message,
    type = "success",
    onClose,
    duration = 3000,
    autoClose = true,
}: ToastProps) {
    const [isExiting, setIsExiting] = useState(false)

    function handleClose() {
        setIsExiting(true)
        setTimeout(onClose, 300) // match with CSS exit animation duration
    }

    useEffect(() => {
        if (!duration) return

        const timer = setTimeout(() => {
            if (autoClose) handleClose()
        }, duration)

        return () => clearTimeout(timer)
    }, [duration, autoClose, onClose])

    return (
        <div className={`toast ${type} ${isExiting ? "exit" : ""}`}>
            <span>{message}</span>
            <button onClick={handleClose} className="toast-close">
                ×
            </button>
        </div>
    )
}