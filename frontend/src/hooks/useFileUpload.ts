import { useState } from "react";
import { useCertService } from "../utils/useCertService";

export const useFileUpload = (onSuccess: () => void) => {
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [password, setPassword] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setDragging] = useState(false);
  const { uploadCertFile } = useCertService();

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setFile(file);
      if (file.name.endsWith(".pfx")) {
        setShowPasswordModal(true);
      } else {
        await uploadFile(file);
      }
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      if (file) {
        setFile(file);
        if (file.name.endsWith(".pfx")) {
          setShowPasswordModal(true);
        } else {
          await uploadFile(file);
        }
      }
    }
  };

  const uploadFile = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const result = await uploadCertFile(file, password);
      setParsedData(result);
      setShowPasswordModal(false);
      setPassword("");
      onSuccess();
      setLoading(false);
    } catch (err:any) {
      if (err.response && err.response.data?.status === "password_required") {
        setError("Incorrect password. Please try again.");
      } else {
        setError("Incorrect password. Please try again.");
      }
    }
    setLoading(false);
  };

  const handlePasswordSubmit = async () => {
    setLoading(true);
    setError(null);
    if (file && password) {
      await uploadFile(file);
    } else {
      setLoading(false);
    }
  };

  const closeModal = () => {
    setShowPasswordModal(false);
    setParsedData(null);
    setPassword("");
    setError(null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
  };

  return {
    showPasswordModal,
    setShowPasswordModal,
    parsedData,
    setPassword,
    password,
    handleDrop,
    handlePasswordSubmit,
    closeModal,
    handleDragOver,
    handleDragLeave,
    loading,
    uploadFile,
    handleFileChange,
    error,
  };
};
