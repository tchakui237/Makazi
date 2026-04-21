"use client";

import { motion } from "framer-motion";
import { ClipboardList, TrendingUp, Building2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-12 relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Logo & Title */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="text-center mb-16"
      >
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
            <Building2 className="w-7 h-7 text-white" strokeWidth={1.5} />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-blue-400 via-emerald-400 to-blue-400 bg-clip-text text-transparent">
              Makazi
            </span>
          </h1>
        </div>
        <p className="text-xl text-slate-300 font-light max-w-md mx-auto">
          Analyse Immobiliere Intelligente pour Yaounde
        </p>
        <p className="text-sm text-slate-500 mt-3 max-w-lg mx-auto">
          Voulez-vous participer a la collecte de donnees ou obtenir une estimation personnalisee ?
        </p>
      </motion.div>

      {/* Two cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl w-full">
        {/* Collect Card */}
        <Link href="/collect" id="card-collect">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="relative group cursor-pointer"
          >
            <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-br from-blue-500/60 to-blue-600/30 opacity-0 group-hover:opacity-100 transition-all duration-500 blur-[2px]" />
            <div className="relative bg-slate-800/80 backdrop-blur-xl rounded-2xl p-8 border border-white/5 group-hover:border-blue-500/20 transition-all duration-500 h-full">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-6 group-hover:shadow-lg group-hover:shadow-blue-500/20 transition-shadow duration-500">
                <ClipboardList className="w-7 h-7 text-white" strokeWidth={1.5} />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3">Collecte</h2>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">
                Participez a la collecte de donnees immobilieres. Chaque contribution ameliore la precision de nos estimations.
              </p>
              <div className="flex items-center gap-2 text-blue-400 text-sm font-medium group-hover:gap-3 transition-all duration-300">
                <span>Commencer</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </motion.div>
        </Link>

        {/* Predict Card */}
        <Link href="/predict" id="card-predict">
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="relative group cursor-pointer"
          >
            <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-br from-emerald-500/60 to-emerald-600/30 opacity-0 group-hover:opacity-100 transition-all duration-500 blur-[2px]" />
            <div className="relative bg-slate-800/80 backdrop-blur-xl rounded-2xl p-8 border border-white/5 group-hover:border-emerald-500/20 transition-all duration-500 h-full">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-6 group-hover:shadow-lg group-hover:shadow-emerald-500/20 transition-shadow duration-500">
                <TrendingUp className="w-7 h-7 text-white" strokeWidth={1.5} />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3">Estimation</h2>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">
                Obtenez une estimation precise du loyer avec intervalle de confiance a 95%, alimentee par notre modele OLS.
              </p>
              <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium group-hover:gap-3 transition-all duration-300">
                <span>Estimer</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </motion.div>
        </Link>
      </div>


    </div>
  );
}
