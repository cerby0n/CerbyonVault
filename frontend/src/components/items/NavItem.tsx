import React from "react";
import { Link, useLocation } from "react-router-dom";

interface NavItemProps {
  icon: React.ReactNode;
  activeIcon: React.ReactNode;
  label: string;
  link: string;
  isOpen: boolean;
}

export default function NavItem({
  icon,
  activeIcon,
  label,
  link,
}: NavItemProps) {
  const location = useLocation();

  const isActive = location.pathname === link;

  return (
    <div className="flex items-center justify-center w-full">
      <Link
        to={link}
        className="group flex flex-col items-center justify-center w-full"
      >
        <div
          className={`
            flex items-center justify-center
           w-10 h-10 mb-1 transition-all duration-150
            ${isActive ? "bg-secondary/25 rounded-xl shadow-sm" : ""}
            group-hover:bg-secondary/25 group-hover:rounded-xl
          `}
        >
          <span className={`text-xl ${isActive ? "text-primary" : "text-primary/60"} group-hover:text-primary`}>
            {isActive ? activeIcon : icon}
          </span>
          </div>
          <span
            className={`text-xs ${
              isActive ? "text-primary" : "text-primary/60"
            }`}
          >
            {label}
          </span>
        
      </Link>
    </div>
  );
}
