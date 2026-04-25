import Modal from "./Modal"

interface ConfirmationModalProps {
  isOpen: boolean
  title?: string
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmationModal({
  isOpen,
  title = "Confirm",
  message,
  onConfirm,
  onCancel,
}: ConfirmationModalProps) {
  return (
    <Modal isOpen={isOpen} title={title} onClose={onCancel}>
      <p>{message}</p>

      <div className="modal-actions">
        <button className="modal-btn cancel" onClick={onCancel}>
          Cancel
        </button>
        <button className="modal-btn confirm" onClick={onConfirm}>
          Confirm
        </button>
      </div>
    </Modal>
  )
}