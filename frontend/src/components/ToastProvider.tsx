import { createContext, useContext, useState } from "react";

type Toast = {
  id: number;
  message: string;
  type: "success" | "error" | "info" | "warning";
};

const ToastContext = createContext<{
  notify: (msg: string, type?: Toast["type"]) => void;
}>({
  notify: () => {},
});

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const notify = (message: string, type: Toast["type"] = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(
      () => setToasts((prev) => prev.filter((t) => t.id !== id)),
      3000
    );
  };

  const alertClassMap: Record<Toast["type"], string> = {
    success: "alert-success",
    error: "alert-error",
    info: "alert-info",
    warning: "alert-warning",
  };

  return (
    <ToastContext.Provider value={{ notify }}>
      {children}
      <div className="toast toast-end toast-bottom mb-10 mr-10 z-[9999]">
        {toasts.map((toast) => (
          <div key={toast.id} className={`alert ${alertClassMap[toast.type]}`}>
            <span>{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
