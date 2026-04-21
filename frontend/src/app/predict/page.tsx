"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Building2,
  ArrowLeft,
  Database,
  BarChart3,
  Target,
  BedDouble,
  ShowerHead,
  Sofa,
  CookingPot,
  Briefcase,
  Droplets,
  Zap,
  Calculator,
} from "lucide-react";
import Link from "next/link";
import StatCard from "@/components/StatCard";
import PriceGauge from "@/components/PriceGauge";
import PriceDistribution from "@/components/PriceDistribution";
import {
  getStats,
  predict,
  getDistribution,
  StatsResponse,
  PredictionResponse,
  DistributionItem,
} from "@/lib/api";

export default function PredictPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [distribution, setDistribution] = useState<DistributionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    type_quartier: "Résidentiel" as
      | "Administratif"
      | "Résidentiel"
      | "Populaire",
    chambres: 3,
    douches: 2,
    salons: 1,
    cuisines: 1,
    bureaux: 0,
    forage: true,
    eneo: true,
  });

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
    getDistribution().then(setDistribution).catch(console.error);
  }, []);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await predict(form);
      setPrediction(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const numberField = (
    label: string,
    icon: React.ReactNode,
    key: keyof typeof form,
    min: number,
    max: number
  ) => (
    <div className="space-y-2">
      <label className="flex items-center gap-2 text-sm text-slate-300 font-medium">
        {icon}
        {label}
      </label>
      <input
        type="number"
        min={min}
        max={max}
        value={form[key] as number}
        onChange={(e) =>
          setForm({ ...form, [key]: parseInt(e.target.value) || 0 })
        }
        className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 transition-all duration-300 hover:border-white/20 focus:border-blue-500/50"
        id={`predict-${key}`}
      />
    </div>
  );

  return (
    <div className="min-h-screen px-6 py-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-10"
      >
        <Link
          href="/"
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">Retour</span>
        </Link>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
            <Building2 className="w-5 h-5 text-white" strokeWidth={1.5} />
          </div>
          <span className="font-semibold text-white">Makazi</span>
        </div>
      </motion.div>

      {/* Stats Dashboard */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          <StatCard
            icon={Database}
            label="Total Entrees"
            value={stats.total_entries}
            gradient="from-blue-500 to-blue-600"
          />
          <StatCard
            icon={BarChart3}
            label="Loyer Moyen"
            value={`${stats.average_price.toLocaleString("fr-FR")} FCFA`}
            gradient="from-emerald-500 to-emerald-600"
          />
          <StatCard
            icon={Target}
            label="R² du Modele"
            value={stats.r_squared?.toFixed(4) ?? "N/A"}
            gradient="from-amber-500 to-amber-600"
          />
        </div>
      )}

      {/* Form + Result */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {/* Prediction Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="relative group"
        >
          <div className="absolute -inset-[1px] rounded-2xl opacity-30 bg-gradient-to-r from-emerald-500 to-blue-500 blur-[1px]" />
          <div className="relative bg-slate-800/90 backdrop-blur-xl rounded-2xl p-8 border border-white/5">
            <h2 className="text-2xl font-bold text-white mb-2">
              Estimation de Loyer
            </h2>
            <p className="text-slate-400 text-sm mb-6">
              Renseignez les caracteristiques pour obtenir une estimation.
            </p>

            <form onSubmit={handlePredict} className="space-y-5">
              {/* Type de quartier */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                  <Building2 className="w-4 h-4 text-emerald-400" />
                  Type de Quartier
                </label>
                <select
                  value={form.type_quartier}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      type_quartier:
                        e.target.value as typeof form.type_quartier,
                    })
                  }
                  className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 text-white transition-all duration-300 hover:border-white/20 focus:border-emerald-500/50 appearance-none cursor-pointer"
                  id="predict-type-quartier"
                >
                  <option value="Administratif">Administratif</option>
                  <option value="Résidentiel">Résidentiel</option>
                  <option value="Populaire">Populaire</option>
                </select>
              </div>

              {/* Numeric fields */}
              <div className="grid grid-cols-2 gap-4">
                {numberField(
                  "Chambres",
                  <BedDouble className="w-4 h-4 text-emerald-400" />,
                  "chambres",
                  0,
                  10
                )}
                {numberField(
                  "Douches",
                  <ShowerHead className="w-4 h-4 text-emerald-400" />,
                  "douches",
                  0,
                  10
                )}
                {numberField(
                  "Salons",
                  <Sofa className="w-4 h-4 text-emerald-400" />,
                  "salons",
                  0,
                  5
                )}
                {numberField(
                  "Cuisines",
                  <CookingPot className="w-4 h-4 text-emerald-400" />,
                  "cuisines",
                  0,
                  5
                )}
                {numberField(
                  "Bureaux",
                  <Briefcase className="w-4 h-4 text-emerald-400" />,
                  "bureaux",
                  0,
                  5
                )}
              </div>

              {/* Toggles */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center justify-between bg-slate-900/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-3">
                    <Droplets className="w-5 h-5 text-blue-400" />
                    <span className="text-sm text-slate-300">Forage</span>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setForm({ ...form, forage: !form.forage })
                    }
                    className={`toggle-switch ${form.forage ? "active" : ""}`}
                    id="predict-toggle-forage"
                  />
                </div>
                <div className="flex items-center justify-between bg-slate-900/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-amber-400" />
                    <span className="text-sm text-slate-300">ENEO</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setForm({ ...form, eneo: !form.eneo })}
                    className={`toggle-switch ${form.eneo ? "active" : ""}`}
                    id="predict-toggle-eneo"
                  />
                </div>
              </div>

              {/* Submit */}
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-semibold py-4 rounded-xl hover:from-emerald-600 hover:to-blue-600 transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                id="btn-predict"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <Calculator className="w-5 h-5" />
                    Estimer le Loyer
                  </>
                )}
              </motion.button>
            </form>
          </div>
        </motion.div>

        {/* Result — Price Gauge */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="relative group"
        >
          <div className="absolute -inset-[1px] rounded-2xl opacity-30 bg-gradient-to-r from-blue-500 to-amber-500 blur-[1px]" />
          <div className="relative bg-slate-800/90 backdrop-blur-xl rounded-2xl p-8 border border-white/5 flex flex-col items-center justify-center min-h-[400px]">
            {prediction ? (
              <PriceGauge
                predicted={prediction.predicted_price}
                lower={prediction.lower_bound}
                upper={prediction.upper_bound}
              />
            ) : (
              <div className="text-center">
                <div className="w-20 h-20 rounded-full bg-slate-700/50 flex items-center justify-center mx-auto mb-4">
                  <Calculator
                    className="w-10 h-10 text-slate-500"
                    strokeWidth={1}
                  />
                </div>
                <p className="text-slate-400 text-sm">
                  Remplissez le formulaire et cliquez sur
                </p>
                <p className="text-slate-400 text-sm">
                  &quot;Estimer le Loyer&quot; pour voir le resultat
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Distribution Chart */}
      {distribution.length > 0 && (
        <PriceDistribution data={distribution} />
      )}
    </div>
  );
}
