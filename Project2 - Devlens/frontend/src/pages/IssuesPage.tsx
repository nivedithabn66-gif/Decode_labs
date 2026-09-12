import React, { useEffect, useState } from 'react';
import {
  Search, Bug, Lightbulb, HelpCircle, AlertTriangle,
  ChevronRight, Filter
} from 'lucide-react';
import type { IssueRecord } from '../types';
import { fetchIssues } from '../services/api';

interface IssuesPageProps {
  onSelectIssue: (id: number) => void;
}

export const IssuesPage: React.FC<IssuesPageProps> = ({ onSelectIssue }) => {
  const [issues, setIssues] = useState<IssueRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [lowConfOnly, setLowConfOnly] = useState<boolean>(false);

  useEffect(() => {
    loadData();
  }, [categoryFilter, lowConfOnly]);

  const loadData = () => {
    setLoading(true);
    const cat = categoryFilter === 'all' ? undefined : categoryFilter;
    const lowConf = lowConfOnly ? true : undefined;

    fetchIssues(cat, undefined, lowConf)
      .then(setIssues)
      .catch((err) => console.error('Fetch issues error:', err))
      .finally(() => setLoading(false));
  };

  const filteredIssues = issues.filter((iss) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return iss.title.toLowerCase().includes(q) || iss.description.toLowerCase().includes(q);
  });

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case 'Bug':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-bold"><Bug className="w-3.5 h-3.5" /><span>Bug</span></span>;
      case 'Feature':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-bold"><Lightbulb className="w-3.5 h-3.5" /><span>Feature</span></span>;
      case 'Question':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold"><HelpCircle className="w-3.5 h-3.5" /><span>Question</span></span>;
      default:
        return <span className="text-xs font-bold text-slate-400">{category}</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold theme-text-main">Triaged Issues Queue</h1>
          <p className="theme-text-sub text-sm mt-1">Browse, search, and inspect classified repository software issues.</p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="theme-card rounded-2xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between shadow-md">
        {/* Search */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 theme-text-muted absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search issue title or description..."
            className="w-full theme-input rounded-xl pl-10 pr-4 py-2 text-xs focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <span className="text-xs theme-text-sub font-semibold mr-1 flex items-center space-x-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Category:</span>
          </span>
          {['all', 'Bug', 'Feature', 'Question'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                categoryFilter === cat
                  ? 'bg-indigo-600 text-white font-bold'
                  : 'theme-card-inner theme-text-sub hover:theme-text-main'
              }`}
            >
              {cat === 'all' ? 'All Issues' : cat}
            </button>
          ))}

          <button
            onClick={() => setLowConfOnly(!lowConfOnly)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center space-x-1.5 cursor-pointer ${
              lowConfOnly
                ? 'bg-amber-500/20 text-amber-600 dark:text-amber-300 border-amber-500/40 font-bold'
                : 'theme-card-inner theme-text-sub hover:theme-text-main'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            <span>Low-Confidence Only</span>
          </button>
        </div>
      </div>

      {/* Issues Table */}
      {loading ? (
        <div className="p-12 text-center theme-text-sub">Loading issues list...</div>
      ) : filteredIssues.length === 0 ? (
        <div className="theme-card rounded-2xl p-12 text-center theme-text-sub">
          No matching issues found in repository database.
        </div>
      ) : (
        <div className="theme-card rounded-2xl overflow-hidden shadow-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="theme-card-inner border-b border-slate-200 dark:border-slate-800 theme-text-sub font-bold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">ID & Title</th>
                  <th className="px-4 py-3.5">Category</th>
                  <th className="px-4 py-3.5">Confidence</th>
                  <th className="px-4 py-3.5">Quality</th>
                  <th className="px-4 py-3.5">Priority</th>
                  <th className="px-4 py-3.5">Team</th>
                  <th className="px-6 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 theme-text-sub">
                {filteredIssues.map((iss) => (
                  <tr key={iss.id} className="hover:bg-slate-100 dark:hover:bg-slate-800/60 transition cursor-pointer" onClick={() => onSelectIssue(iss.id)}>
                    <td className="px-6 py-4">
                      <div className="flex items-start space-x-2">
                        <span className="font-mono theme-text-muted font-bold">#{iss.id}</span>
                        <div>
                          <span className="font-bold theme-text-main text-sm block">{iss.title}</span>
                          <span className="theme-text-sub text-[11px] line-clamp-1">{iss.description}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">{getCategoryBadge(iss.predicted_category)}</td>
                    <td className="px-4 py-4">
                      <div className="flex items-center space-x-1.5 font-mono font-semibold">
                        <span>{(iss.confidence * 100).toFixed(1)}%</span>
                        {iss.is_low_confidence && (
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="font-bold theme-text-main">{iss.quality_score}</span>
                      <span className="theme-text-muted">/100</span>
                    </td>
                    <td className="px-4 py-4 font-semibold">
                      <span className={
                        iss.priority_recommendation === 'Critical' ? 'text-red-500' :
                        iss.priority_recommendation === 'High' ? 'text-amber-500' : 'text-blue-500'
                      }>
                        {iss.priority_recommendation || 'Medium'}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-indigo-600 dark:text-indigo-400 font-semibold">{iss.team_recommendation || 'Backend'}</td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-1.5 rounded-lg theme-card-inner text-indigo-600 dark:text-indigo-400 transition cursor-pointer">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

