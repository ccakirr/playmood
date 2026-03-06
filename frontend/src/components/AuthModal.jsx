import { useState } from "react";
import { useAuthStore } from "../store/useAuthStore";

/**
 * Modal for login / register.
 * Props:
 *   isOpen   – boolean
 *   onClose  – () => void
 *   onSuccess – () => void  (called after successful auth so parent can retry)
 */
const AuthModal = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuthStore();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggle = () => {
    setMode((m) => (m === "login" ? "register" : "login"));
    setError("");
  };

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      onClick={onClose}
    >
      {/* Card – stop propagation so clicking inside doesn't close */}
      <div
        className="w-full max-w-sm rounded-2xl border border-base-200 bg-base-100 shadow-2xl p-8 space-y-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="space-y-1">
          <h2 className="text-2xl font-bold">
            {mode === "login" ? "Welcome back" : "Create account"}
          </h2>
          <p className="text-sm text-base-content/60">
            {mode === "login"
              ? "Sign in to save your playlists."
              : "Sign up to save and revisit your playlists."}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Email</label>
            <input
              type="email"
              required
              autoComplete="email"
              className="input input-bordered w-full"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Password</label>
            <input
              type="password"
              required
              minLength={6}
              autoComplete={
                mode === "login" ? "current-password" : "new-password"
              }
              className="input input-bordered w-full"
              placeholder="min. 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <div className="rounded-lg bg-error/10 border border-error/30 px-4 py-2 text-sm text-error">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? (
              <span className="loading loading-spinner loading-sm" />
            ) : null}
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        {/* Toggle */}
        <p className="text-center text-sm text-base-content/60">
          {mode === "login"
            ? "Don't have an account?"
            : "Already have an account?"}{" "}
          <button
            onClick={toggle}
            className="text-primary font-medium hover:underline"
          >
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>

        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 btn btn-ghost btn-sm btn-circle"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default AuthModal;
