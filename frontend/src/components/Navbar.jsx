import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import ThemeController from "./ThemeController";
import AuthModal from "./AuthModal";
import { useAuthStore } from "../store/useAuthStore";

const Navbar = () => {
  const { user, logout } = useAuthStore();
  const [scrolled, setScrolled] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Glass effect on scroll
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const avatarInitial = user?.email?.[0]?.toUpperCase() ?? "?";

  return (
    <>
    <div
      className={`navbar sticky top-0 z-40 transition-all duration-300 ${
        scrolled
          ? "bg-base-100/70 backdrop-blur-lg shadow-md border-b border-base-200/50"
          : "bg-base-100 shadow-sm"
      }`}
    >
      <div className="mx-auto flex w-full max-w-6xl items-center px-4">
        {/* Logo */}
        <div className="navbar-start">
          <Link
            to="/"
            className="text-3xl font-semibold font-mono tracking-tight select-none"
          >
            Play<span className="text-primary">Mood</span>
          </Link>
        </div>

        <div className="navbar-center hidden flex-1 lg:flex" />

        {/* Right side */}
        <div className="navbar-end flex items-center gap-2">
          {user ? (
            <>
              <Link
                to="/my-playlists"
                className="btn btn-ghost btn-sm hidden sm:flex"
              >
                My Playlists
              </Link>

              {/* Avatar + Dropdown */}
              <div className="relative" ref={dropdownRef}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setDropdownOpen((o) => !o)}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-content font-bold text-sm shadow select-none cursor-pointer"
                  aria-label="Account menu"
                >
                  {avatarInitial}
                </motion.button>

                <AnimatePresence>
                  {dropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -8, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -8, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-2 w-52 rounded-xl border border-base-200 bg-base-100/90 backdrop-blur-md shadow-xl overflow-hidden"
                    >
                      {/* User info */}
                      <div className="px-4 py-3 border-b border-base-200">
                        <p className="text-xs text-base-content/50 truncate">
                          Signed in as
                        </p>
                        <p className="text-sm font-medium truncate">
                          {user.email}
                        </p>
                      </div>

                      <Link
                        to="/my-playlists"
                        onClick={() => setDropdownOpen(false)}
                        className="flex items-center gap-2 px-4 py-2.5 text-sm hover:bg-base-200/60 transition-colors"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                          />
                        </svg>
                        My Playlists
                      </Link>

                      <button
                        onClick={() => {
                          logout();
                          setDropdownOpen(false);
                        }}
                        className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-error hover:bg-error/10 transition-colors"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
                          />
                        </svg>
                        Sign out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </>
          ) : (
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => setAuthOpen(true)}
              className="btn btn-primary btn-sm px-5"
            >
              Sign in
            </motion.button>
          )}

          <ThemeController />
        </div>
      </div>
    </div>

    <AuthModal
      isOpen={authOpen}
      onClose={() => setAuthOpen(false)}
      onSuccess={() => setAuthOpen(false)}
    />
    </>
  );
};

export default Navbar;
