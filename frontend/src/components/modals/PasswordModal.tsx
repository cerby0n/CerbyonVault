type PasswordModalProps = {
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handlePasswordSubmit: () => void;
  closeModal: () => void;
  loading: boolean;
  error: string |null;
};

export default function PasswordModal({
  password,
  setPassword,
  handlePasswordSubmit,
  closeModal,
  loading,
  error,
}: PasswordModalProps) {
  return (
      <div className="modal modal-open backdrop-blur-xs overflow-hidden">
        <div className="modal-box bg-base-100 overflow-hidden">
          <h3 className="font-bold text-secondary-content text-lg">Enter Password for PFX</h3>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="input input-bordered w-full mt-4"
          />
          {error && <div className="text-error text-sm mt-2">{error}</div>}
          <div className="modal-action">
            <button className="btn btn-outline" onClick={closeModal}>
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={handlePasswordSubmit}
              disabled={loading}
            >
              {loading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </div>
      </div>
  );
}
