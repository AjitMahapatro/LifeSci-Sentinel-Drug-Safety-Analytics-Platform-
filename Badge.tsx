import { RISK_COLORS } from "../theme";
import { clsx } from "clsx";
import type { RiskLevel } from "../types";

interface BadgeProps {
  label: string;
  variant?: "default" | "risk" | "quality";
  riskLevel?: RiskLevel;
  className?: string;
}

export function Badge({
  label,
  variant = "default",
  riskLevel,
  className = "",
}: BadgeProps) {
  return (
    <span
      className={clsx(
        "text-xs font-semibold inline-flex items-center px-2.5 py-0.5 rounded-full",
        {
          "bg-gray-100 text-gray-800": variant === "default" || (variant === "risk" && !riskLevel),
          "bg-teal-100 text-teal-800": variant === "quality",
          ...(variant === "risk" && riskLevel && { [RISK_COLORS[riskLevel].badge]: true }),
        },
        className
      )}
    >
      {label}
    </span>
  );
}