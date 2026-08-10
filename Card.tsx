import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  padding?: "default" | "none";
}

export function Card({ children, className = "", title, padding = "default" }: CardProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        </div>
      )}
      <div className={padding === "default" ? "p-6" : ""}>{children}</div>
    </div>
  );
}