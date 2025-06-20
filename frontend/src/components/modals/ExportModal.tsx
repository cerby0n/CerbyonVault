import { useState } from "react";

type ExportModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onDownload: (
    variant: ExportVariant,
    format: ExportFormat,
    password?: string
  ) => void;
  hasPrivateKey: boolean,
  certName:string,
};

type ExportFormat = "pem" | "crt" | "pfx";
type ExportVariant = "cert" | "cert+key" | "chain" | "chain+key";

export default function ExportModal({
  isOpen,
  onClose,
  onDownload,
  hasPrivateKey,
  certName,
}: ExportModalProps) {
  const [variant, setVariant] = useState<ExportVariant>("cert");
  const [format, setFormat] = useState<ExportFormat>("pem");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const availableFormats: ExportFormat[] =
    variant === "cert" || variant === "chain"
      ? ["pem", "crt"]
      : ["pem", "crt", "pfx"];

  const handleDownload = () => {
    if (format === "pfx" && password !== confirmPassword) {
      setPasswordError("❌ Passwords do not match.");
      return;
    }

    onDownload(variant, format, format === "pfx" ? password : undefined);
    setPasswordError("");
    onClose();

    // Reset
    setVariant("cert");
    setFormat("pem");
    setPassword("");
    setConfirmPassword("");
  };

  if (!isOpen) return null;

  return (
    <dialog className="modal modal-open backdrop-blur-xs">
      <div className="modal-box w-full max-w-md">
        <h3 className="font-bold text-lg mb-4">📁 Export {certName ? `"${certName}"` : "Certificate"}</h3>

        <div className="flex justify-between space-x-10">
          {/* Variant Selection */}
          <div className=" mb-4 flex-1">
            <label className="label">Export Type:</label>
            <select
              className="select"
              value={variant}
              onChange={(e) => setVariant(e.target.value as ExportVariant)}
            >
              <option value="cert">Cert</option>
              {hasPrivateKey && <option value="cert+key">Cert + Key</option>}
              <option value="chain">Chain</option>
              {hasPrivateKey && <option value="chain+key">Chain + Key</option>}
            </select>
          </div>

          {/* Format Selection */}
          <div className="mb-4 flex-1">
            <label className="label">Format:</label>
            <select
              className="select"
              value={format}
              onChange={(e) => setFormat(e.target.value as ExportFormat)}
            >
              {availableFormats.map((f) => (
                <option key={f} value={f}>
                  {f.toUpperCase()} (
                  {f === "pem" ? ".pem" : f === "crt" ? ".crt" : ".pfx"})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Password (if PFX) */}
        {format === "pfx" && (
          <>
            <div className="form-control mb-2 flex flex-col">
              <label className="label">Password:</label>
              <input
                type="password"
                className="input input-bordered w-full"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="form-control mb-4 flex flex-col">
              <label className="label">Confirm Password:</label>
              <input
                type="password"
                className="input input-bordered w-full"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            {passwordError && (
              <p className="text-error text-sm mt-1">{passwordError}</p>
            )}
          </>
        )}

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleDownload}>
            Download
          </button>
        </div>
      </div>
    </dialog>
  );
}
