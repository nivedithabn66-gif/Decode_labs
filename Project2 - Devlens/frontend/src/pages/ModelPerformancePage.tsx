import React, { useEffect, useState } from 'react';
import { CheckCircle2, Award } from 'lucide-react';
import { fetchModelMetrics } from '../services/api';

export const ModelPerformancePage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModelMetrics()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-12 text-center text-slate-400">Loading model evaluation metrics...</div>;
  if (!data || !data.metadata) return <div className="p-12 text-center text-slate-400">No model evaluation metadata available.</div>;

  const meta = data.metadata;
  const perClass = data.per_class_report || {};
  const cm = data.confusion_matrix || {};

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
            Supervised ML Evaluation
          </span>
        </div>
        <h1 className="text-3xl font-extrabold theme-text-main mt-2">Model Performance & Algorithm Comparison</h1>
        <p className="theme-text-sub text-sm mt-1">
          Comparative evaluation across Linear SVM, Logistic Regression, Naive Bayes, and Random Forest classifiers.
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="theme-card rounded-2xl p-5 space-y-1 shadow-md">
          <span className="text-xs font-bold theme-text-sub uppercase tracking-wider block">Selected Classifier</span>
          <span className="text-xl font-extrabold theme-text-main">{meta.model_name}</span>
          <span className="text-xs text-indigo-600 dark:text-indigo-400 font-mono block">Version {meta.version}</span>
        </div>

        <div className="theme-card rounded-2xl p-5 space-y-1 shadow-md">
          <span className="text-xs font-bold theme-text-sub uppercase tracking-wider block">Primary Selection Metric</span>
          <span className="text-xl font-extrabold text-emerald-600 dark:text-emerald-400">Macro F1 Score</span>
          <span className="text-xs theme-text-sub block font-mono">{(meta.best_macro_f1 * 100).toFixed(1)}%</span>
        </div>

        <div className="theme-card rounded-2xl p-5 space-y-1 shadow-md">
          <span className="text-xs font-bold theme-text-sub uppercase tracking-wider block">Overall Accuracy</span>
          <span className="text-xl font-extrabold theme-text-main">{(meta.best_accuracy * 100).toFixed(1)}%</span>
          <span className="text-xs theme-text-muted block">Multiclass Evaluation</span>
        </div>

        <div className="theme-card rounded-2xl p-5 space-y-1 shadow-md">
          <span className="text-xs font-bold theme-text-sub uppercase tracking-wider block">Dataset & Features</span>
          <span className="text-xl font-extrabold theme-text-main">{meta.train_samples} Train / {meta.test_samples} Test</span>
          <span className="text-xs theme-text-sub block font-mono">{meta.num_features} TF-IDF Features</span>
        </div>
      </div>

      {/* Model Comparison Table */}
      <div className="theme-card rounded-2xl overflow-hidden shadow-md space-y-4 p-6">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <h2 className="text-base font-bold theme-text-main flex items-center space-x-2">
            <Award className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>Candidate Models Benchmark Comparison</span>
          </h2>
          <span className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold">Primary Metric: MACRO F1</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="theme-card-inner border-b border-slate-200 dark:border-slate-800 theme-text-sub font-bold uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Model</th>
                <th className="px-4 py-3">Accuracy</th>
                <th className="px-4 py-3">Macro F1</th>
                <th className="px-4 py-3">Weighted F1</th>
                <th className="px-4 py-3">Train Time</th>
                <th className="px-4 py-3">Latency</th>
                <th className="px-4 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 theme-text-sub font-mono">
              {meta.candidate_comparisons.map((row: any, idx: number) => {
                const isSelected = row.model_name === meta.model_name;
                return (
                  <tr key={idx} className={isSelected ? 'bg-indigo-500/10 font-bold theme-text-main' : ''}>
                    <td className="px-4 py-3.5 font-sans font-semibold flex items-center space-x-2">
                      <span>{row.model_name}</span>
                    </td>
                    <td className="px-4 py-3.5">{(row.accuracy * 100).toFixed(2)}%</td>
                    <td className="px-4 py-3.5 text-emerald-600 dark:text-emerald-400">{(row.macro_f1 * 100).toFixed(2)}%</td>
                    <td className="px-4 py-3.5">{(row.weighted_f1 * 100).toFixed(2)}%</td>
                    <td className="px-4 py-3.5">{row.train_time_sec}s</td>
                    <td className="px-4 py-3.5">{row.pred_latency_ms}ms</td>
                    <td className="px-4 py-3.5 text-right font-sans">
                      {isSelected ? (
                        <span className="inline-flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 text-xs bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-bold">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>SELECTED</span>
                        </span>
                      ) : (
                        <span className="theme-text-muted text-xs">Evaluated</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per Class Metrics & Confusion Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Per Class Breakdown */}
        <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h3 className="text-base font-bold theme-text-main border-b border-slate-200 dark:border-slate-800 pb-3">Per-Class Classification Metrics</h3>
          <div className="space-y-3">
            {Object.keys(perClass).map((clsKey) => {
              const item = perClass[clsKey];
              return (
                <div key={clsKey} className="p-3 theme-card-inner rounded-xl space-y-2">
                  <div className="flex justify-between font-bold text-xs">
                    <span className="text-indigo-600 dark:text-indigo-400">{clsKey}</span>
                    <span className="theme-text-sub">Support: {item.support}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                    <div className="theme-card p-2 rounded">
                      <span className="theme-text-muted text-[10px] block">PRECISION</span>
                      <span className="font-bold theme-text-main">{(item.precision * 100).toFixed(1)}%</span>
                    </div>
                    <div className="theme-card p-2 rounded">
                      <span className="theme-text-muted text-[10px] block">RECALL</span>
                      <span className="font-bold theme-text-main">{(item.recall * 100).toFixed(1)}%</span>
                    </div>
                    <div className="theme-card p-2 rounded">
                      <span className="theme-text-muted text-[10px] block">F1-SCORE</span>
                      <span className="font-bold text-emerald-600 dark:text-emerald-400">{(item.f1 * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Confusion Matrix */}
        <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h3 className="text-base font-bold theme-text-main border-b border-slate-200 dark:border-slate-800 pb-3">Confusion Matrix</h3>
          {cm.matrix ? (
            <div className="space-y-3">
              <div className="grid grid-cols-4 gap-2 text-center text-xs font-bold theme-text-sub">
                <div></div>
                {cm.labels.map((l: string) => <div key={l}>{l}</div>)}
              </div>
              {cm.matrix.map((row: number[], rowIdx: number) => (
                <div key={rowIdx} className="grid grid-cols-4 gap-2 text-center text-xs font-mono items-center">
                  <div className="font-bold theme-text-sub text-left pl-2">{cm.labels[rowIdx]}</div>
                  {row.map((val: number, colIdx: number) => (
                    <div
                      key={colIdx}
                      className={`p-3 rounded-lg border font-extrabold ${
                        rowIdx === colIdx
                          ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border-emerald-500/30'
                          : val > 0 ? 'bg-red-500/20 text-red-600 dark:text-red-300 border-red-500/30' : 'theme-card-inner theme-text-muted'
                      }`}
                    >
                      {val}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          ) : (
            <p className="theme-text-muted text-xs">No confusion matrix data available.</p>
          )}
        </div>
      </div>
    </div>
  );
};

