"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";
import { motion } from "framer-motion";
import { DistributionItem } from "@/lib/api";

interface PriceDistributionProps {
  data: DistributionItem[];
}

const COLORS: Record<string, string> = {
  Administratif: "#3b82f6",
  "Résidentiel": "#10b981",
  Populaire: "#f59e0b",
};

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div className="bg-slate-800/95 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-xl">
        <p className="text-white font-semibold text-sm">{d.type_quartier}</p>
        <div className="mt-2 space-y-1">
          <p className="text-slate-300 text-xs">
            Nombre : <span className="text-white font-medium">{d.count}</span>
          </p>
          <p className="text-slate-300 text-xs">
            Moyenne :{" "}
            <span className="text-white font-medium">
              {d.average.toLocaleString("fr-FR")} FCFA
            </span>
          </p>
          <p className="text-slate-300 text-xs">
            Min :{" "}
            <span className="text-white font-medium">
              {d.min.toLocaleString("fr-FR")} FCFA
            </span>
          </p>
          <p className="text-slate-300 text-xs">
            Max :{" "}
            <span className="text-white font-medium">
              {d.max.toLocaleString("fr-FR")} FCFA
            </span>
          </p>
        </div>
      </div>
    );
  }
  return null;
};

export default function PriceDistribution({ data }: PriceDistributionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="relative group"
    >
      <div className="absolute -inset-[1px] rounded-2xl opacity-30 group-hover:opacity-50 transition-opacity duration-500 blur-[1px] bg-gradient-to-r from-blue-500 via-emerald-500 to-amber-500" />
      <div className="relative bg-slate-800/90 backdrop-blur-xl rounded-2xl p-6 border border-white/5">
        <h3 className="text-lg font-semibold text-white mb-6">
          Distribution des loyers par type de quartier
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(148,163,184,0.1)"
            />
            <XAxis
              dataKey="type_quartier"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              axisLine={{ stroke: "rgba(148,163,184,0.2)" }}
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              axisLine={{ stroke: "rgba(148,163,184,0.2)" }}
              tickFormatter={(v) =>
                v >= 1000 ? `${Math.round(v / 1000)}K` : v
              }
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(148,163,184,0.05)" }} />
            <Bar dataKey="average" radius={[8, 8, 0, 0]} maxBarSize={80}>
              {data.map((entry, index) => (
                <Cell
                  key={index}
                  fill={COLORS[entry.type_quartier] || "#6366f1"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
