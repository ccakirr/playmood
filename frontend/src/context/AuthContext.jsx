import { createContext, useContext } from "react";
import { useAuthStore } from "../store/useAuthStore";

/**
 * AuthContext – React Context katmanı.
 *
 * useAuthStore (Zustand) tek gerçek kaynak olmaya devam eder; bu context,
 * store'u React Context API aracılığıyla tüketen bileşenler için ince bir
 * sarmalayıcı sağlar. Her iki API da birlikte kullanılabilir.
 *
 * Kullanım:
 *   const { user, token, login, logout, ... } = useAuth();
 */

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const auth = useAuthStore();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
};
