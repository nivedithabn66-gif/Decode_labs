import React, { useEffect, useState } from 'react';
import { CheckCircle2 } from 'lucide-react';
import type { ErrorSample } from '../types';
import { fetchErrorSamples } from '../services/api';

export const ErrorAnalysisPage: React.FC = () => {
  const [samples, setSamples] = useState<ErrorSample[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCat, setFilterCat] = useState<string>('all');

  useEffect(() => {
    fetchErrorSamples()
      .then(setSamples)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filteredSamples = samples.filter((s) => {
    if (filterCat === 'all') return true;
    return s.actual === filterCat || s.predicted === filterCat;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-widest bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20">
              Error Analysis Workbench
            </span>
          </div>
          <h1 className="text-3xl font-extrabold theme-text-main mt-2">Model Misclassification Audit</h1>
          <p className="theme-text-sub text-sm mt-1">
            Inspect model prediction errors, low-confidence instances, and category confusion patterns for iterative ML pipeline improvement.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs theme-text-sub font-semibold">Filter Category:</span>
          {['all', 'Bug', 'Feature', 'Question'].map((c) => (
            <button
              key={c}
              onClick={() => setFilterCat(c)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition cursor-pointer ${
                filterCat === c ? 'bg-indigo-600 text-white font-bold' : 'theme-card-inner theme-text-sub hover:theme-text-main'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center theme-text-sub">Loading error analysis samples...</div>
      ) : filteredSamples.length === 0 ? (
        <div className="theme-card rounded-2xl p-12 text-center theme-text-sub space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400 mx-auto" />
          <h3 className="text-lg font-bold theme-text-main">No Evaluation Errors Found</h3>
          <p className="text-xs theme-text-sub">The current trained model achieved 100% accuracy on test set benchmark evaluations.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredSamples.map((sample) => (
            <div key={sample.id} className="theme-card rounded-2xl p-5 space-y-3 shadow-md">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
                <span className="font-mono text-xs font-bold theme-text-muted">Test Instance #{sample.id}</span>
                <span className="text-xs font-mono font-semibold text-amber-600 dark:text-amber-400">
                  Confidence: {(sample.confidence * 100).toFixed(1)}%
                </span>
              </div>

              <h3 className="text-base font-bold theme-text-main">{sample.title}</h3>
              <p className="theme-text-sub text-xs theme-card-inner p-3 rounded-xl border font-mono">
                {sample.text_snippet}
              </p>

              <div className="flex items-center justify-between text-xs pt-1">
                <div className="flex items-center space-x-4">
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Actual Label: <strong>{sample.actual}</strong></span>
                  <span className="text-red-500 font-semibold">Predicted Label: <strong>{sample.predicted}</strong></span>
                </div>

                <span className="text-amber-600 dark:text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                  Misclassified
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

