import { createContext, useContext, useState, useCallback } from "react";
import { AnimatePresence, motion as Motion } from "framer-motion";

// ── Context ───────────────────────────────────────────────────────────────────
const ToastContext = createContext(null);

let _id = 0;

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ message, type = "success", duration = 3500 }) => {
    const id = ++_id;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {/* Toast stack — top-right */}
      <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        <AnimatePresence mode="popLayout">
          {toasts.map((t) => (
            <Motion.div
              key={t.id}
              layout
              initial={{ opacity: 0, x: 60, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 60, scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
              className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-sm font-medium min-w-[240px] max-w-xs backdrop-blur-md
                ${t.type === "success" ? "bg-success/15 border-success/30 text-success" : ""}
                ${t.type === "error"   ? "bg-error/15 border-error/30 text-error" : ""}
                ${t.type === "info"    ? "bg-info/15 border-info/30 text-info" : ""}
              `}
            >
              {/* Icon */}
              {t.type === "success" && (
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
              {t.type === "error" && (
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              {t.type === "info" && (
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01" />
                  <circle cx="12" cy="12" r="9" strokeLinecap="round" />
                </svg>
              )}
              <span className="flex-1">{t.message}</span>
              <button
                onClick={() => removeToast(t.id)}
                className="opacity-50 hover:opacity-100 transition-opacity"
                aria-label="Dismiss"
              >
                ✕
              </button>
            </Motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>");
  return ctx;
};
