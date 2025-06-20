interface ConfirmModalProps {
  message: string | React.ReactNode;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function ConfirmModal({
  message,
  onCancel,
  onConfirm,
}: ConfirmModalProps) {
  return (
    <dialog open className="modal backdrop-blur-xs">
      <div className="modal-box">
        <h3 className="font-bold text-lg">Confirm Deletion</h3>
        <p className="py-4">{message}</p>
        <div className="modal-action">
          <button className="btn" onClick={onCancel}>Cancel</button>
          <button className="btn btn-error" onClick={onConfirm}>Delete</button>
        </div>
      </div>
    </dialog>
  );
}