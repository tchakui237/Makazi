"use client";

import { motion } from "framer-motion";

interface PriceGaugeProps {
  predicted: number;
  lower: number;
  upper: number;
  min?: number;
  max?: number;
}

export default function PriceGauge({
  predicted,
  lower,
  upper,
  min = 0,
  max = 600000,
}: PriceGaugeProps) {
  const range = max - min;
  const angle = ((predicted - min) / range) * 180;
  const lowerAngle = ((lower - min) / range) * 180;
  const upperAngle = ((upper - min) / range) * 180;

  const polarToCartesian = (
    cx: number,
    cy: number,
    r: number,
    deg: number
  ) => {
    const rad = ((180 - deg) * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy - r * Math.sin(rad),
    };
  };

  const describeArc = (
    cx: number,
    cy: number,
    r: number,
    startDeg: number,
    endDeg: number
  ) => {
    const start = polarToCartesian(cx, cy, r, endDeg);
    const end = polarToCartesian(cx, cy, r, startDeg);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
  };

  const cx = 160;
  const cy = 140;
  const r = 110;

  const needleEnd = polarToCartesian(cx, cy, r - 10, angle);
  const needleBase1 = polarToCartesian(cx, cy, 6, angle + 90);
  const needleBase2 = polarToCartesian(cx, cy, 6, angle - 90);

  const formatPrice = (price: number) => {
    if (price >= 1000000) return `${(price / 1000000).toFixed(1)}M`;
    if (price >= 1000) return `${Math.round(price / 1000)}K`;
    return price.toString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="flex flex-col items-center"
    >
      <svg viewBox="0 0 320 180" className="w-full max-w-[360px]">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background arc */}
        <path
          d={describeArc(cx, cy, r, 0, 180)}
          fill="none"
          stroke="rgba(148,163,184,0.15)"
          strokeWidth="20"
          strokeLinecap="round"
        />

        {/* Colored arc */}
        <motion.path
          d={describeArc(cx, cy, r, 0, 180)}
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth="20"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, ease: "easeInOut" }}
        />

        {/* Confidence interval arc */}
        <path
          d={describeArc(cx, cy, r, lowerAngle, upperAngle)}
          fill="none"
          stroke="rgba(59,130,246,0.5)"
          strokeWidth="28"
          strokeLinecap="round"
          opacity="0.3"
        />

        {/* Needle */}
        <motion.polygon
          points={`${needleEnd.x},${needleEnd.y} ${needleBase1.x},${needleBase1.y} ${needleBase2.x},${needleBase2.y}`}
          fill="#f8fafc"
          filter="url(#glow)"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.4 }}
        />

        {/* Center dot */}
        <circle cx={cx} cy={cy} r="8" fill="#3b82f6" />
        <circle cx={cx} cy={cy} r="4" fill="#f8fafc" />

        {/* Labels */}
        <text x="30" y="158" fill="#94a3b8" fontSize="11" fontFamily="Inter">
          {formatPrice(min)}
        </text>
        <text x="260" y="158" fill="#94a3b8" fontSize="11" fontFamily="Inter">
          {formatPrice(max)}
        </text>
      </svg>

      {/* Price display */}
      <motion.div
        className="text-center -mt-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.4 }}
      >
        <p className="text-3xl font-bold text-white">
          {predicted.toLocaleString("fr-FR")} FCFA
        </p>
        <p className="text-sm text-slate-400 mt-2">
          Fourchette estimee entre{" "}
          <span className="text-blue-400 font-semibold">
            {lower.toLocaleString("fr-FR")}
          </span>{" "}
          et{" "}
          <span className="text-blue-400 font-semibold">
            {upper.toLocaleString("fr-FR")}
          </span>{" "}
          FCFA
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Intervalle de confiance a 95%
        </p>
      </motion.div>
    </motion.div>
  );
}
