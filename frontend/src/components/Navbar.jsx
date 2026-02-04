import React from "react";
import ThemeController from "./ThemeController";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <div className="navbar bg-base-100 shadow-sm">
      <div className="mx-auto flex w-full max-w-6xl items-center px-4">
        <div className="navbar-start">
          <Link to="/" className="text-3xl font-semibold font-mono tracking-tight">
            Play<span className=" text-primary">Mood</span>
          </Link>
        </div>
        <div className="navbar-center hidden flex-1 lg:flex"></div>
        <div className="navbar-end">
          <ThemeController />
        </div>
      </div>
    </div>
  );
};

export default Navbar;
