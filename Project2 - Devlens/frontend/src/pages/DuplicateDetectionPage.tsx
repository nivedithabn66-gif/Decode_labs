import React, { useState } from 'react';
import { CopyCheck, Search, CheckCircle2, ArrowRightLeft } from 'lucide-react';
import type { DuplicateMatch, IssueCompareResponse } from '../types';
import { compareIssues } from '../services/api';

export const DuplicateDetectionPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Comparison State
  const [compTitleA, setCompTitleA] = useState('Application crashes when uploading large file');
  const [compDescA, setCompDescA] = useState('NullPointerException thrown in FileHandler.java line 42 when uploading >5MB file.');
  const [compTitleB, setCompTitleB] = useState('Server fails on big file uploads');
  const [compDescB, setCompDescB] = useState('Upload process freezes with 500 error when sending large attachments.');
  const [compLoading, setCompLoading] = useState(false);
  const [compResult, setCompResult] = useState<IssueCompareResponse | null>(null);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/issues/duplicate-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, threshold: 0.35 })
      });
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      alert('Duplicate check failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    setCompLoading(true);
    try {
      const res = await compareIssues(compTitleA, compDescA, compTitleB, compDescB);
      setCompResult(res);
    } catch (err: any) {
      alert('Comparison failed: ' + err.message);
    } finally {
      setCompLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6">
        <h1 className="text-3xl font-extrabold theme-text-main">Duplicate Detection & Issue Comparison</h1>
        <p className="theme-text-sub text-sm mt-1">
          TF-IDF Vectorization & Cosine Similarity search against existing issue repositories, with side-by-side diff comparison.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <form onSubmit={handleCheck} className="lg:col-span-6 theme-card rounded-2xl p-6 space-y-4 shadow-md">
          <h2 className="text-base font-bold theme-text-main flex items-center space-x-2">
            <CopyCheck className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>Search Repository Similarity</span>
          </h2>

          <div>
            <label className="block text-xs font-semibold theme-text-sub uppercase tracking-wider mb-1">Issue Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Application crashes during file upload"
              className="w-full theme-input rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold theme-text-sub uppercase tracking-wider mb-1">Issue Description</label>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter issue description..."
              className="w-full theme-input rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition cursor-pointer"
          >
            <Search className="w-4 h-4" />
            <span>RUN SIMILARITY SEARCH</span>
          </button>
        </form>

        <div className="lg:col-span-6 space-y-4">
          {!result && !loading && (
            <div className="theme-card rounded-2xl p-8 text-center theme-text-sub min-h-[300px] flex items-center justify-center">
              Enter issue title and description to run TF-IDF cosine similarity search.
            </div>
          )}

          {loading && (
            <div className="theme-card rounded-2xl p-8 text-center theme-text-sub min-h-[300px] flex items-center justify-center">
              Searching repository vectors...
            </div>
          )}

          {result && !loading && (
            <div className="theme-card rounded-2xl p-6 space-y-4 shadow-md">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-bold theme-text-main">Search Results</h3>
                <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400">
                  Max Similarity: {result.max_similarity_percentage}%
                </span>
              </div>

              {result.potential_duplicates.length === 0 ? (
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>No similar existing issues matched high similarity thresholds.</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {result.potential_duplicates.map((item: DuplicateMatch) => (
                    <div key={item.issue_id} className="p-4 rounded-xl theme-card-inner space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">Issue #{item.issue_id}</span>
                        <span className="text-xs font-bold theme-text-main theme-card px-2 py-0.5 rounded">
                          {item.similarity_percentage}% Similarity
                        </span>
                      </div>
                      <h4 className="text-sm font-bold theme-text-main">{item.title}</h4>
                      <div className="flex items-center space-x-2 text-[11px] theme-text-sub pt-1">
                        <span>Category: {item.category}</span>
                        <span>•</span>
                        <span>Date: {item.created_at}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Side-by-Side Issue Comparison Workbench */}
      <div className="theme-card rounded-2xl p-6 space-y-6 shadow-md">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold theme-text-main flex items-center space-x-2">
              <ArrowRightLeft className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span>Side-by-Side Issue Comparison Workbench</span>
            </h2>
            <p className="text-xs theme-text-sub">Compare two issue reports side-by-side to highlight common terms, error signals, and category alignment.</p>
          </div>
          <button
            onClick={handleCompare}
            disabled={compLoading}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg transition cursor-pointer"
          >
            {compLoading ? 'Comparing...' : 'RUN SIDE-BY-SIDE DIFF'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Issue A */}
          <div className="theme-card-inner rounded-xl p-4 space-y-3">
            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block">ISSUE A (New Issue)</span>
            <input
              type="text"
              value={compTitleA}
              onChange={(e) => setCompTitleA(e.target.value)}
              className="w-full theme-input rounded-lg px-3 py-1.5 text-xs"
            />
            <textarea
              rows={3}
              value={compDescA}
              onChange={(e) => setCompDescA(e.target.value)}
              className="w-full theme-input rounded-lg px-3 py-1.5 text-xs"
            />
          </div>

          {/* Issue B */}
          <div className="theme-card-inner rounded-xl p-4 space-y-3">
            <span className="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider block">ISSUE B (Existing / Candidate Issue)</span>
            <input
              type="text"
              value={compTitleB}
              onChange={(e) => setCompTitleB(e.target.value)}
              className="w-full theme-input rounded-lg px-3 py-1.5 text-xs"
            />
            <textarea
              rows={3}
              value={compDescB}
              onChange={(e) => setCompDescB(e.target.value)}
              className="w-full theme-input rounded-lg px-3 py-1.5 text-xs"
            />
          </div>
        </div>

        {/* Comparison Output Results */}
        {compResult && (
          <div className="theme-card-inner rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold theme-text-main">Comparison Summary</span>
              <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400 font-bold bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
                Overlapping Similarity: {compResult.similarity_percentage}%
              </span>
            </div>
            <p className="text-xs theme-text-sub">{compResult.comparison_summary}</p>
            {compResult.common_terms.length > 0 && (
              <div>
                <span className="text-[11px] font-semibold theme-text-sub block mb-1">Shared Key Terms & Context Signals:</span>
                <div className="flex flex-wrap gap-1.5">
                  {compResult.common_terms.map((term, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20 font-mono">
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};


