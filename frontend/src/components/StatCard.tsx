"use client";

import { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  gradient: string;
}

export default function StatCard({
  icon: Icon,
  label,
  value,
  gradient,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative group"
    >
      {/* Gradient border glow */}
      <div
        className={`absolute -inset-[1px] rounded-2xl opacity-50 group-hover:opacity-100 transition-opacity duration-500 blur-[1px] ${gradient}`}
      />

      {/* Card content */}
      <div className="relative bg-slate-800/90 backdrop-blur-xl rounded-2xl p-6 border border-white/5">
        <div className="flex items-center gap-4">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br ${gradient}`}
          >
            <Icon className="w-6 h-6 text-white" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-sm text-slate-400 font-medium">{label}</p>
            <p className="text-2xl font-bold text-white mt-0.5">{value}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
