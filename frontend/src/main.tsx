import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ToastProvider } from "./components/ToastProvider";
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
  <ToastProvider>
    <App />
  </ToastProvider>
  </StrictMode>
);
