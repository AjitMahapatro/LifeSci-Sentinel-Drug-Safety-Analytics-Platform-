import type { RiskLevel } from "./types";

export const RISK_COLORS: Record<RiskLevel, { text: string; bg: string; border: string; badge: string }> = {
  LOW: {
    text: "text-gray-800",
    bg: "bg-gray-50",
    border: "border-gray-300",
    badge: "bg-gray-100 text-gray-800",
  },
  MODERATE: {
    text: "text-yellow-800",
    bg: "bg-yellow-50",
    border: "border-yellow-400",
    badge: "bg-yellow-100 text-yellow-800",
  },
  HIGH: {
    text: "text-orange-800",
    bg: "bg-orange-50",
    border: "border-orange-400",
    badge: "bg-orange-100 text-orange-800",
  },
  CRITICAL: {
    text: "text-red-800",
    bg: "bg-red-50",
    border: "border-red-500",
    badge: "bg-red-100 text-red-800",
  },
};