"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
  Banknote,
  CheckCircle2,
  Send,
  AlertCircle, // <-- Ajout de l'icône d'erreur
} from "lucide-react";
import Link from "next/link";
import StatCard from "@/components/StatCard";
import { collectData, getStats, StatsResponse } from "@/lib/api";

export default function CollectPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null); // <-- Nouvel état pour l'erreur
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    type_quartier: "Résidentiel" as "Administratif" | "Résidentiel" | "Populaire",
    chambres: 2,
    douches: 1,
    salons: 1,
    cuisines: 1,
    bureaux: 0,
    forage: false,
    eneo: true,
    loyer: 100000,
  });

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null); // On réinitialise l'erreur à chaque tentative
    setSuccess(false);
    
    try {
      await collectData(form);
      const newStats = await getStats();
      setStats(newStats);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 4000);
      
      // On réinitialise le formulaire après un succès
      setForm({
        type_quartier: "Résidentiel",
        chambres: 2,
        douches: 1,
        salons: 1,
        cuisines: 1,
        bureaux: 0,
        forage: false,
        eneo: true,
        loyer: 100000,
      });
    } catch (err: any) {
      console.error(err);
      // On capte le message envoyé par lib/api.ts et on l'affiche
      setErrorMsg(err.message || "Une erreur est survenue lors de la connexion au serveur.");
      setTimeout(() => setErrorMsg(null), 6000); // L'erreur disparaît après 6s
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
        id={`field-${key}`}
      />
    </div>
  );

  return (
    <div className="min-h-screen px-6 py-8 max-w-5xl mx-auto">
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

      {/* Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="relative group"
      >
        <div className="absolute -inset-[1px] rounded-2xl opacity-30 bg-gradient-to-r from-blue-500 to-emerald-500 blur-[1px]" />
        <div className="relative bg-slate-800/90 backdrop-blur-xl rounded-2xl p-8 border border-white/5">
          <h2 className="text-2xl font-bold text-white mb-2">
            Formulaire de Collecte
          </h2>
          <p className="text-slate-400 text-sm mb-8">
            Renseignez les caracteristiques de l&apos;appartement pour
            alimenter notre base de donnees.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Type de quartier */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                <Building2 className="w-4 h-4 text-blue-400" />
                Type de Quartier
              </label>
              <select
                value={form.type_quartier}
                onChange={(e) =>
                  setForm({
                    ...form,
                    type_quartier: e.target.value as typeof form.type_quartier,
                  })
                }
                className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 text-white transition-all duration-300 hover:border-white/20 focus:border-blue-500/50 appearance-none cursor-pointer"
                id="field-type-quartier"
              >
                <option value="Administratif">Administratif</option>
                <option value="Résidentiel">Résidentiel</option>
                <option value="Populaire">Populaire</option>
              </select>
            </div>

            {/* Numeric fields grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {numberField(
                "Chambres",
                <BedDouble className="w-4 h-4 text-blue-400" />,
                "chambres",
                0,
                10
              )}
              {numberField(
                "Douches",
                <ShowerHead className="w-4 h-4 text-blue-400" />,
                "douches",
                0,
                10
              )}
              {numberField(
                "Salons",
                <Sofa className="w-4 h-4 text-blue-400" />,
                "salons",
                0,
                5
              )}
              {numberField(
                "Cuisines",
                <CookingPot className="w-4 h-4 text-blue-400" />,
                "cuisines",
                0,
                5
              )}
              {numberField(
                "Bureaux",
                <Briefcase className="w-4 h-4 text-blue-400" />,
                "bureaux",
                0,
                5
              )}
            </div>

            {/* Toggle switches */}
            <div className="grid grid-cols-2 gap-6">
              <div className="flex items-center justify-between bg-slate-900/30 rounded-xl p-4 border border-white/5">
                <div className="flex items-center gap-3">
                  <Droplets className="w-5 h-5 text-blue-400" />
                  <span className="text-sm text-slate-300">Forage</span>
                </div>
                <button
                  type="button"
                  onClick={() => setForm({ ...form, forage: !form.forage })}
                  className={`w-12 h-6 rounded-full transition-colors relative ${form.forage ? "bg-emerald-500" : "bg-slate-700"}`}
                  id="toggle-forage"
                >
                  <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${form.forage ? "translate-x-6" : ""}`} />
                </button>
              </div>
              <div className="flex items-center justify-between bg-slate-900/30 rounded-xl p-4 border border-white/5">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <span className="text-sm text-slate-300">ENEO</span>
                </div>
                <button
                  type="button"
                  onClick={() => setForm({ ...form, eneo: !form.eneo })}
                  className={`w-12 h-6 rounded-full transition-colors relative ${form.eneo ? "bg-emerald-500" : "bg-slate-700"}`}
                  id="toggle-eneo"
                >
                  <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${form.eneo ? "translate-x-6" : ""}`} />
                </button>
              </div>
            </div>

            {/* Loyer */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                <Banknote className="w-4 h-4 text-emerald-400" />
                Loyer Mensuel (FCFA)
              </label>
              <input
                type="number"
                min={1}
                value={form.loyer}
                onChange={(e) =>
                  setForm({
                    ...form,
                    loyer: parseInt(e.target.value) || 0,
                  })
                }
                className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 transition-all duration-300 hover:border-white/20 focus:border-blue-500/50"
                id="field-loyer"
              />
            </div>

            {/* Submit */}
            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-semibold py-4 rounded-xl hover:from-blue-600 hover:to-emerald-600 transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              id="btn-submit-collect"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Soumettre
                </>
              )}
            </motion.button>
          </form>
        </div>
      </motion.div>

      {/* Notifications Système (Z-index élevé pour passer au-dessus du reste) */}
      <AnimatePresence>
        {/* Notification de SUCCÈS */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-emerald-500/90 backdrop-blur-xl text-white px-6 py-4 rounded-xl flex items-center gap-3 shadow-2xl shadow-emerald-500/20 z-50"
          >
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-medium">Données enregistrées avec succès</span>
          </motion.div>
        )}

        {/* Notification d'ERREUR Pydantic (Le fameux 422) */}
        {errorMsg && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-rose-500/90 backdrop-blur-xl text-white px-6 py-4 rounded-xl flex items-center gap-3 shadow-2xl shadow-rose-500/20 z-50"
          >
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span className="font-medium text-sm">{errorMsg}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
