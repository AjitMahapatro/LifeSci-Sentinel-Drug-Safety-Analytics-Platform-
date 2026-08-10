import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { name: "Overview", path: "/" },
  { name: "Drug Investigation", path: "/drugs" },
  { name: "Safety Signals", path: "/signals" },
  { name: "AI Assistant", path: "/ai" },
];

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <span className="font-bold text-xl text-navy-700">🧬 LifeSci Sentinel</span>
              <div className="hidden md:flex space-x-8">
                {navItems.map((item) => (
                  <NavLink key={item.name} to={item.path} className={({ isActive }) => `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}>{item.name}</NavLink>
                ))}
              </div>
            </div>
          </div>
        </nav>
      </header>
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}