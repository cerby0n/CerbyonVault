import { useState } from "react";
import { useFileUpload } from "../../hooks/useFileUpload";
import PasswordModal from "./PasswordModal";
import CertImportModal from "./CertImportModal";

interface CertUploadModalProps {
  closeCertModal: () => void;
  setShowCertUploadModal: (value: boolean) => void;
  fetchFunction: () => void;
}

export default function CertUploadModal({
  closeCertModal,
  setShowCertUploadModal,
  fetchFunction,
}: CertUploadModalProps) {
  const [dragging, setDragging] = useState(false);

  const {
    showPasswordModal,
    parsedData,
    setPassword,
    password,
    handleDrop,
    handlePasswordSubmit,
    closeModal,
    loading,
    handleFileChange,
    error,
  } = useFileUpload(() => fetchFunction());

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const onSuccess = () => {
    setShowCertUploadModal(false);
    fetchFunction();
  };

  return (
    <div className="modal modal-open backdrop-blur-xs">
      {/* Password Modal for PFX Files */}
      {showPasswordModal && (
        <PasswordModal
          password={password}
          setPassword={setPassword}
          handlePasswordSubmit={handlePasswordSubmit}
          closeModal={closeModal}
          loading={loading}
          error={error}
        />
      )}
      <div className="modal-box w-full max-w-3xl bg-base-100">
        <h2 className="font-bold text-xl mb-4 text-secondary-content">Upload Certificate</h2>

        {/* Drag-and-drop Area for Modal Only */}
        <div
          className={`border-2 border-dashed p-8 text-center text-secondary-content ${
            dragging ? "border-primary" : "border-secondary/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <p className="text-sm mb-8">Drag & Drop Certificate here or</p>
          <input
            type="file"
            className="hidden"
            id="file-upload"
            onChange={handleFileChange}
          />
          <label
            htmlFor="file-upload"
            className="btn btn-primary cursor-pointer"
          >
            Browse File
          </label>
        </div>

        {/* Upload Button */}
        <div className="modal-action">
          <button className="btn btn-outline" onClick={closeCertModal}>
            Cancel
          </button>
        </div>
      </div>
      {/* CertImportModal for Successful Upload */}
      {parsedData && (
        <CertImportModal
          session_key={parsedData.session_key}
          certificates={parsedData.certificates}
          private_key={parsedData.private_key}
          onSubmit={async () => {
            closeModal();
            onSuccess();
          }}
          onCancel={closeModal}
        />
      )}
    </div>
  );
}
