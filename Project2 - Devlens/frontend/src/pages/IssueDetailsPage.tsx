import React, { useEffect, useState } from 'react';
import {
  ArrowLeft, CheckCircle2, Send, MessageSquare
} from 'lucide-react';
import type { IssueRecord, IssueCategory } from '../types';
import { fetchIssueDetails, submitFeedback } from '../services/api';

interface IssueDetailsPageProps {
  issueId: number;
  onBack: () => void;
}

export const IssueDetailsPage: React.FC<IssueDetailsPageProps> = ({ issueId, onBack }) => {
  const [issue, setIssue] = useState<IssueRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [correctedLabel, setCorrectedLabel] = useState<IssueCategory>('Feature');
  const [feedbackComment, setFeedbackComment] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchIssueDetails(issueId)
      .then((data) => {
        setIssue(data);
        setCorrectedLabel(data.predicted_category === 'Bug' ? 'Feature' : 'Bug');
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [issueId]);

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!issue) return;

    setSubmittingFeedback(true);
    try {
      const res = await submitFeedback(issue.id, issue.predicted_category, correctedLabel, feedbackComment);
      setFeedbackSuccess(res.message || 'Feedback recorded successfully.');
      setIssue({ ...issue, predicted_category: correctedLabel });
    } catch (err: any) {
      alert(err.message || 'Feedback submission failed.');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (loading) return <div className="p-12 text-center text-slate-400">Loading Issue details...</div>;
  if (!issue) return <div className="p-12 text-center text-slate-400">Issue not found.</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-xs font-semibold theme-text-sub hover:theme-text-main transition cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Issues Queue</span>
      </button>

      <div className="theme-card rounded-2xl p-6 space-y-6 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-sm font-bold theme-text-muted">Issue #{issue.id}</span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                issue.predicted_category === 'Bug' ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20' :
                issue.predicted_category === 'Feature' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20' : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
              }`}>
                {issue.predicted_category}
              </span>
            </div>
            <h1 className="text-2xl font-extrabold theme-text-main mt-1">{issue.title}</h1>
          </div>

          <div className="text-right">
            <span className="text-xs theme-text-sub block">ML Confidence</span>
            <span className="text-2xl font-extrabold theme-text-main">{(issue.confidence * 100).toFixed(1)}%</span>
          </div>
        </div>

        {/* Issue Text Content */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider theme-text-sub mb-1">Description</h3>
            <p className="theme-text-main text-sm leading-relaxed theme-card-inner p-4 rounded-xl border font-sans">
              {issue.description}
            </p>
          </div>

          {issue.steps_to_reproduce && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider theme-text-sub mb-1">Steps to Reproduce</h3>
              <p className="theme-text-sub text-xs theme-card-inner p-3 rounded-lg border font-mono whitespace-pre-line">
                {issue.steps_to_reproduce}
              </p>
            </div>
          )}

          {issue.logs && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider theme-text-sub mb-1">Error Logs / Stacktrace</h3>
              <p className="text-red-600 dark:text-red-300 text-xs theme-card-inner p-3 rounded-lg border border-red-500/30 font-mono overflow-x-auto">
                {issue.logs}
              </p>
            </div>
          )}
        </div>

        {/* Triage Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-200 dark:border-slate-800">
          <div>
            <span className="text-[11px] theme-text-muted uppercase font-bold block">Quality Score</span>
            <span className="text-lg font-bold theme-text-main">{issue.quality_score} / 100</span>
          </div>
          <div>
            <span className="text-[11px] theme-text-muted uppercase font-bold block">Priority</span>
            <span className="text-lg font-bold text-amber-500">{issue.priority_recommendation || 'Medium'}</span>
          </div>
          <div>
            <span className="text-[11px] theme-text-muted uppercase font-bold block">Suggested Team</span>
            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{issue.team_recommendation || 'Backend'}</span>
          </div>
          <div>
            <span className="text-[11px] theme-text-muted uppercase font-bold block">Model Version</span>
            <span className="text-lg font-bold theme-text-sub font-mono">{issue.model_version}</span>
          </div>
        </div>
      </div>

      {/* Human-in-the-Loop Feedback Widget */}
      <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
        <div className="flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <MessageSquare className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-base font-bold theme-text-main">Human-in-the-Loop Prediction Correction</h3>
        </div>

        {feedbackSuccess ? (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-sm font-semibold flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5" />
            <span>{feedbackSuccess}</span>
          </div>
        ) : (
          <form onSubmit={handleFeedbackSubmit} className="space-y-4">
            <p className="text-xs theme-text-sub">
              Was DevLens's ML prediction incorrect? Submit a correction to record in the feedback dataset for controlled retraining.
            </p>

            <div className="flex items-center space-x-4">
              <span className="text-xs theme-text-sub font-semibold">Correct Category to:</span>
              {(['Bug', 'Feature', 'Question'] as IssueCategory[]).map((cat) => (
                <button
                  type="button"
                  key={cat}
                  onClick={() => setCorrectedLabel(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer ${
                    correctedLabel === cat
                      ? 'bg-indigo-600 text-white font-bold'
                      : 'theme-card-inner theme-text-sub hover:theme-text-main'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <textarea
              rows={2}
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
              placeholder="Optional developer feedback note..."
              className="w-full theme-input rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
            />

            <button
              type="submit"
              disabled={submittingFeedback}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition cursor-pointer"
            >
              <Send className="w-4 h-4" />
              <span>SUBMIT CORRECTION</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

