"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

export type ToastType = "info" | "success" | "warning" | "error";

interface ToastMessage {
  id: string;
  text: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (text: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = useCallback((text: string, type: ToastType = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
    setToasts((prev) => [...prev.slice(-3), { id, text, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3200);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Notification Container (Bottom-Right, Zero Rounding, Industrial Styling) */}
      <div
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full font-mono text-[12px]"
        aria-live="polite"
      >
        {toasts.map((toast) => {
          const borderColor =
            toast.type === "success"
              ? "border-[#FF6B35]"
              : toast.type === "error"
              ? "border-[#FF4D4D]"
              : toast.type === "warning"
              ? "border-[#FFB800]"
              : "border-[var(--border-main)]";

          const badgeColor =
            toast.type === "success"
              ? "text-[#FF6B35]"
              : toast.type === "error"
              ? "text-[#FF4D4D]"
              : toast.type === "warning"
              ? "text-[#FFB800]"
              : "text-[var(--text-muted)]";

          return (
            <div
              key={toast.id}
              className={`p-3 bg-[var(--bg-surface)] border ${borderColor} text-[var(--text-main)] shadow-none transition-all duration-200 pointer-events-auto flex items-start gap-2.5 animate-in fade-in slide-in-from-bottom-2`}
              role="status"
            >
              <span className={`font-bold ${badgeColor}`}>
                {toast.type === "success" ? "✓" : toast.type === "error" ? "✕" : "ℹ"}
              </span>
              <span className="flex-1 leading-snug">{toast.text}</span>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};
