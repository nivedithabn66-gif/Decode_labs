import React, { useEffect, useState } from 'react';
import { Database, Cpu, Sliders, CheckCircle2, Sun, Moon, Monitor, Archive } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { fetchModelRegistry } from '../services/api';
import type { ModelRegistryItem } from '../types';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [threshold, setThreshold] = useState(0.65);
  const [apiHost, setApiHost] = useState('http://localhost:8000/api');
  const [saved, setSaved] = useState(false);
  const [registry, setRegistry] = useState<ModelRegistryItem[]>([]);

  useEffect(() => {
    fetchModelRegistry()
      .then((data) => setRegistry(data.registry))
      .catch(console.error);
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6">
        <h1 className="text-3xl font-extrabold theme-text-main">DevLens Platform Settings & Registry</h1>
        <p className="theme-text-sub text-sm mt-1">Configure ML threshold parameters, theme preferences, Model Registry, and backend connection details.</p>
      </div>

      {saved && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>Configuration saved successfully.</span>
        </div>
      )}

      {/* Theme Preference Card */}
      <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
        <h2 className="text-base font-bold theme-text-main flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <Sun className="w-5 h-5 text-amber-500" />
          <span>Interface Theme Mode</span>
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <button
            type="button"
            onClick={() => setTheme('dark')}
            className={`p-4 rounded-xl border flex flex-col items-center justify-center space-y-2 transition cursor-pointer ${
              theme === 'dark' ? 'bg-indigo-600/20 border-indigo-500 theme-text-main font-bold' : 'theme-card-inner theme-text-sub hover:opacity-90'
            }`}
          >
            <Moon className="w-6 h-6 text-indigo-500 dark:text-indigo-400" />
            <span className="text-xs">Dark Theme</span>
          </button>

          <button
            type="button"
            onClick={() => setTheme('light')}
            className={`p-4 rounded-xl border flex flex-col items-center justify-center space-y-2 transition cursor-pointer ${
              theme === 'light' ? 'bg-indigo-600/20 border-indigo-500 theme-text-main font-bold' : 'theme-card-inner theme-text-sub hover:opacity-90'
            }`}
          >
            <Sun className="w-6 h-6 text-amber-500" />
            <span className="text-xs">Light Theme</span>
          </button>

          <button
            type="button"
            onClick={() => setTheme('system')}
            className={`p-4 rounded-xl border flex flex-col items-center justify-center space-y-2 transition cursor-pointer ${
              theme === 'system' ? 'bg-indigo-600/20 border-indigo-500 theme-text-main font-bold' : 'theme-card-inner theme-text-sub hover:opacity-90'
            }`}
          >
            <Monitor className="w-6 h-6 theme-text-muted" />
            <span className="text-xs">System Preference</span>
          </button>
        </div>
      </div>

      {/* Model Registry Panel */}
      <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
        <h2 className="text-base font-bold theme-text-main flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Archive className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>Model Version Registry</span>
          </div>
          <span className="text-xs theme-text-sub">Total Versions: {registry.length}</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="theme-card-inner theme-text-sub font-bold uppercase tracking-wider">
              <tr>
                <th className="p-3">Version</th>
                <th className="p-3">Model Name</th>
                <th className="p-3">Macro F1</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Training Date</th>
                <th className="p-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800 font-mono theme-text-sub">
              {registry.map((item, i) => (
                <tr key={i} className={item.is_active ? 'bg-indigo-500/10 font-bold theme-text-main' : ''}>
                  <td className="p-3 text-indigo-600 dark:text-indigo-400 font-sans">{item.version}</td>
                  <td className="p-3 font-sans font-semibold">{item.model_name}</td>
                  <td className="p-3 text-emerald-600 dark:text-emerald-400">{(item.macro_f1 * 100).toFixed(1)}%</td>
                  <td className="p-3">{(item.accuracy * 100).toFixed(1)}%</td>
                  <td className="p-3 theme-text-muted">{item.training_date}</td>
                  <td className="p-3 text-right font-sans">
                    {item.is_active ? (
                      <span className="text-emerald-600 dark:text-emerald-400 text-xs bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-bold">
                        ACTIVE PRODUCTION
                      </span>
                    ) : (
                      <span className="theme-text-muted text-xs">ARCHIVED</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* ML Thresholds */}
        <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h2 className="text-base font-bold theme-text-main flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <Sliders className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>ML Confidence & Triage Parameters</span>
          </h2>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span className="theme-text-main">Low-Confidence Indicator Threshold</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-mono">{(threshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.4"
              max="0.9"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-2 theme-card-inner rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <p className="text-[11px] theme-text-muted">Predictions below this score will trigger manual review warnings.</p>
          </div>
        </div>

        {/* System & Preprocessing */}
        <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h2 className="text-base font-bold theme-text-main flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <Cpu className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>NLP Pipeline Configuration</span>
          </h2>

          <div className="grid grid-cols-2 gap-4 text-xs font-semibold">
            <div className="p-3 theme-card-inner rounded-xl border">
              <span className="theme-text-muted block">Lowercase Normalization:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-mono">ENABLED</span>
            </div>

            <div className="p-3 theme-card-inner rounded-xl border">
              <span className="theme-text-muted block">Whitespace Normalization:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-mono">ENABLED</span>
            </div>

            <div className="p-3 theme-card-inner rounded-xl border">
              <span className="theme-text-muted block">English Stopword Removal:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-mono">ENABLED</span>
            </div>

            <div className="p-3 theme-card-inner rounded-xl border">
              <span className="theme-text-muted block">Primary Feature Extraction:</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-mono">TF-IDF (Unigrams + Bigrams)</span>
            </div>
          </div>
        </div>

        {/* Backend API Host */}
        <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h2 className="text-base font-bold theme-text-main flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>FastAPI Server Connection</span>
          </h2>

          <div>
            <label className="block text-xs font-semibold theme-text-sub uppercase tracking-wider mb-1">API Base Endpoint</label>
            <input
              type="text"
              value={apiHost}
              onChange={(e) => setApiHost(e.target.value)}
              className="w-full theme-input rounded-xl px-4 py-2 text-xs font-mono focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <button
          type="submit"
          className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition cursor-pointer"
        >
          SAVE SETTINGS
        </button>
      </form>
    </div>
  );
};


