import React, { useEffect, useState } from 'react';
import {
  LayoutDashboard, Bug, Lightbulb, HelpCircle,
  BarChart3, Cpu, ArrowRight, Sparkles, AlertTriangle
} from 'lucide-react';
import type { DashboardStats, ModelHealth, DistributionShift } from '../types';
import { fetchDashboardStats, fetchModelHealth, fetchDistributionShift } from '../services/api';

interface DashboardPageProps {
  setActiveTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ setActiveTab }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<ModelHealth | null>(null);
  const [shift, setShift] = useState<DistributionShift | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchDashboardStats(),
      fetchModelHealth(),
      fetchDistributionShift()
    ]).then(([s, h, sh]) => {
      setStats(s);
      setHealth(h);
      setShift(sh);
    }).catch((err) => console.error('Dashboard stats error:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
              Developer Triage Platform
            </span>
          </div>
          <h1 className="text-3xl font-extrabold theme-text-main mt-2">DevLens Developer Dashboard</h1>
          <p className="theme-text-sub text-sm mt-1">
            Real-time GitHub issue classification analytics, confidence tracking, quality scoring, and ML model evaluation.
          </p>
        </div>

        <button
          onClick={() => setActiveTab('analyze')}
          className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm tracking-wide shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition self-start md:self-auto cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Analyze New Issue</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Distribution Shift Banner */}
      {shift && shift.has_data_shift && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-300 flex items-center justify-between">
          <div className="flex items-center space-x-3 text-xs">
            <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
            <div>
              <span className="font-bold block text-sm">Potential Data Distribution Shift Detected</span>
              <span>Production predictions deviate significantly from training dataset class ratios. Consider retraining model.</span>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('settings')}
            className="text-xs bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-700 dark:text-amber-200 px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer"
          >
            Review Retraining
          </button>
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center theme-text-sub font-medium">Loading Dashboard Analytics...</div>
      ) : stats ? (
        <>
          {/* Top Metric Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Issues Card */}
            <div className="theme-card rounded-2xl p-5 space-y-2 shadow-sm">
              <div className="flex items-center justify-between theme-text-sub">
                <span className="text-xs font-bold uppercase tracking-wider">Total Issues</span>
                <LayoutDashboard className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div className="text-3xl font-extrabold theme-text-main">{stats.total_issues}</div>
              <span className="text-xs theme-text-muted block">Triaged across repository</span>
            </div>

            {/* Bugs Card */}
            <div className="theme-card rounded-2xl p-5 space-y-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-red-500 dark:text-red-400">Bugs</span>
                <Bug className="w-5 h-5 text-red-500 dark:text-red-400" />
              </div>
              <div className="text-3xl font-extrabold theme-text-main">{stats.bugs}</div>
              <span className="text-xs theme-text-sub">
                {((stats.bugs / maxOne(stats.total_issues)) * 100).toFixed(1)}% of total queue
              </span>
            </div>

            {/* Features Card */}
            <div className="theme-card rounded-2xl p-5 space-y-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-500 dark:text-blue-400">Features</span>
                <Lightbulb className="w-5 h-5 text-blue-500 dark:text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold theme-text-main">{stats.features}</div>
              <span className="text-xs theme-text-sub">
                {((stats.features / maxOne(stats.total_issues)) * 100).toFixed(1)}% of total queue
              </span>
            </div>

            {/* Questions Card */}
            <div className="theme-card rounded-2xl p-5 space-y-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-500 dark:text-emerald-400">Questions</span>
                <HelpCircle className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold theme-text-main">{stats.questions}</div>
              <span className="text-xs theme-text-sub">
                {((stats.questions / maxOne(stats.total_issues)) * 100).toFixed(1)}% of total queue
              </span>
            </div>
          </div>

          {/* Second Row Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Category Breakdown Bar Visual */}
            <div className="md:col-span-2 theme-card rounded-2xl p-6 space-y-4 shadow-md">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <h3 className="text-base font-bold theme-text-main flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  <span>Issue Category Distribution</span>
                </h3>
                <span className="text-xs theme-text-sub">Primary Classifier Output</span>
              </div>

              <div className="space-y-4 py-2">
                {/* Bug Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-red-500 dark:text-red-400 flex items-center space-x-1.5">
                      <Bug className="w-3.5 h-3.5" />
                      <span>Bug (Dataset Label 0)</span>
                    </span>
                    <span className="theme-text-main font-mono">{stats.bugs} issues</span>
                  </div>
                  <div className="w-full theme-card-inner rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-red-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${(stats.bugs / maxOne(stats.total_issues)) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Feature Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-blue-500 dark:text-blue-400 flex items-center space-x-1.5">
                      <Lightbulb className="w-3.5 h-3.5" />
                      <span>Feature (Dataset Label 1)</span>
                    </span>
                    <span className="theme-text-main font-mono">{stats.features} issues</span>
                  </div>
                  <div className="w-full theme-card-inner rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-blue-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${(stats.features / maxOne(stats.total_issues)) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Question Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-emerald-500 dark:text-emerald-400 flex items-center space-x-1.5">
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>Question (Dataset Label 2)</span>
                    </span>
                    <span className="theme-text-main font-mono">{stats.questions} issues</span>
                  </div>
                  <div className="w-full theme-card-inner rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${(stats.questions / maxOne(stats.total_issues)) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Model & Quality Summary Card */}
            <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                  <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400">
                    <Cpu className="w-5 h-5" />
                    <h3 className="text-base font-bold theme-text-main">Active Model Metrics</h3>
                  </div>
                  {health && (
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                      {health.model_status}
                    </span>
                  )}
                </div>

                <div className="mt-4 space-y-3">
                  <div className="flex justify-between text-xs">
                    <span className="theme-text-sub">Deployed Classifier:</span>
                    <span className="theme-text-main font-bold">{stats.current_model}</span>
                  </div>

                  <div className="flex justify-between text-xs">
                    <span className="theme-text-sub">Model Version:</span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-mono font-semibold">{stats.model_version}</span>
                  </div>

                  <div className="flex justify-between text-xs">
                    <span className="theme-text-sub">Macro F1 Score:</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">{(stats.macro_f1 * 100).toFixed(1)}%</span>
                  </div>

                  <div className="flex justify-between text-xs">
                    <span className="theme-text-sub">Avg Issue Quality:</span>
                    <span className="theme-text-main font-bold">{stats.avg_quality_score} / 100</span>
                  </div>

                  <div className="flex justify-between text-xs">
                    <span className="theme-text-sub">Low-Confidence Rate:</span>
                    <span className="text-amber-500 font-bold">{stats.low_confidence_rate}%</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setActiveTab('performance')}
                className="w-full py-2.5 rounded-xl theme-card-inner hover:opacity-90 text-xs theme-text-main font-semibold transition flex items-center justify-center space-x-1 cursor-pointer"
              >
                <span>Inspect Full Evaluation Report</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};



function maxOne(num: number): number {
  return num === 0 ? 1 : num;
}
