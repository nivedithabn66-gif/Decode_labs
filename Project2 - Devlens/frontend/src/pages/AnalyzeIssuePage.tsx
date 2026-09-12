import React, { useState, useRef } from 'react';
import {
  Bug, Lightbulb, HelpCircle, Sparkles, CheckCircle2,
  AlertTriangle, CopyCheck, RotateCcw, Send, UploadCloud,
  FileText, FileArchive, Wrench, Code2
} from 'lucide-react';
import type { IssueAnalyzeRequest, IssueAnalyzeResponse } from '../types';
import { analyzeIssue, analyzeFileIssue, createIssue } from '../services/api';

interface AnalyzeIssuePageProps {
  onIssueCreated?: () => void;
}

export const AnalyzeIssuePage: React.FC<AnalyzeIssuePageProps> = ({ onIssueCreated }) => {
  const [formData, setFormData] = useState<IssueAnalyzeRequest>({
    title: '',
    description: '',
    steps_to_reproduce: '',
    expected_behavior: '',
    actual_behavior: '',
    environment: '',
    version: '',
    logs: ''
  });

  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<IssueAnalyzeResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    setSelectedFile(file);
    setLoading(true);
    setSubmitSuccess(null);
    try {
      const res = await analyzeFileIssue(file);
      setAnalysisResult(res);
      setFormData({
        title: res.title,
        description: res.extracted_file_info?.description_snippet || res.title,
        steps_to_reproduce: 'Extracted from file attachment: ' + file.name,
        expected_behavior: '',
        actual_behavior: '',
        environment: res.extracted_file_info?.file_type || '',
        version: '',
        logs: res.important_signals.join('\n')
      });
    } catch (err: any) {
      alert('Failed to extract and analyze file: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const sampleInputs = [
    {
      label: 'Sample Bug',
      data: {
        title: 'Application crashes when uploading large file',
        description: 'When uploading a PNG image larger than 5MB, the backend service throws a NullPointerException in FileHandler.java line 42. The upload progress freezes and returns HTTP 500 error.',
        steps_to_reproduce: '1. Navigate to upload screen\n2. Select 10MB test image\n3. Click Submit Upload',
        expected_behavior: 'File uploads cleanly and displays preview thumbnail.',
        actual_behavior: 'System freezes, returns HTTP 500 server exception.',
        environment: 'Windows 11, Chrome 120, Python 3.14',
        version: 'v2.1.0',
        logs: 'java.lang.NullPointerException: File parameter is null at FileHandler.upload(FileHandler.java:42)'
      }
    },
    {
      label: 'Sample Feature',
      data: {
        title: 'Please add dark mode toggle to navigation header',
        description: 'Add dark mode support with automatic system preference detection. Users should be able to toggle themes and persist settings in local storage across browser sessions.',
        steps_to_reproduce: 'N/A - New feature request.',
        expected_behavior: 'Header includes theme toggle button with light/dark/system mode options.',
        actual_behavior: 'Only default light theme is currently supported.',
        environment: 'All browsers',
        version: 'v2.2.0-beta',
        logs: ''
      }
    },
    {
      label: 'Sample Question',
      data: {
        title: 'How can I configure authentication token expiration times?',
        description: 'Where in config.yaml or environment settings can I modify the default JWT access token lifetime from 15 minutes to 60 minutes for local development?',
        steps_to_reproduce: '',
        expected_behavior: '',
        actual_behavior: '',
        environment: 'FastAPI Backend',
        version: 'v1.0.0',
        logs: ''
      }
    },
    {
      label: 'Memory Leak Bug',
      data: {
        title: 'Memory leak in WebSocket real-time issue streaming connection handler',
        description: 'Long-running client WebSocket connections cause RAM memory usage to grow continuously until Linux OOM killer terminates node process after 2 hours of streaming.',
        steps_to_reproduce: '1. Open streaming dashboard\n2. Connect 50 concurrent sockets\n3. Monitor server RSS memory over 60 mins',
        expected_behavior: 'Memory consumption stabilizes at ~150MB RSS under constant load.',
        actual_behavior: 'Memory leaks continuously past 4GB until process crashes with OOM error.',
        environment: 'Ubuntu 22.04 LTS, Node.js v20.10.0',
        version: 'v1.4.2',
        logs: 'FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory\n1: 0xb83d20 node::Abort() [node]'
      }
    },
    {
      label: 'Report Export Feature',
      data: {
        title: 'Export issue triage reports to PDF and CSV format',
        description: 'Engineering managers need an export button in the dashboard to download monthly issue classification summary reports and team allocation metrics in CSV and PDF formats.',
        steps_to_reproduce: 'N/A - Feature request for reporting analytics.',
        expected_behavior: 'Download button generates structured PDF report with charts and raw issue CSV file.',
        actual_behavior: 'Reports can only be viewed in browser dashboard.',
        environment: 'React Dashboard / Next.js',
        version: 'v2.3.0',
        logs: ''
      }
    },
    {
      label: 'Docker Migrations Question',
      data: {
        title: 'How to execute database migrations inside Docker Compose startup?',
        description: 'What is the recommended approach to run Alembic migration scripts automatically before starting the Uvicorn FastAPI web server inside containerized deployment?',
        steps_to_reproduce: '',
        expected_behavior: 'DB schema updates automatically on container start before accepting incoming traffic.',
        actual_behavior: 'Need clarification on docker-entrypoint.sh script ordering.',
        environment: 'Docker 24.0.7, PostgreSQL 16',
        version: 'v1.0.0',
        logs: ''
      }
    },
    {
      label: 'Rate Limiter Security Bug',
      data: {
        title: 'API rate limiter fails to block excessive login retry attempts',
        description: 'Brute force requests on /api/v1/auth/login are not rate limited properly when X-Forwarded-For HTTP proxy headers are sent by malicious clients.',
        steps_to_reproduce: '1. Send 100 HTTP POST requests to /api/v1/auth/login with random passwords\n2. Mutate X-Forwarded-For header on each request',
        expected_behavior: 'Client IP is blocked with HTTP 429 Too Many Requests after 5 failed attempts.',
        actual_behavior: 'Rate limiter bypass occurs because header spoofing circumvents IP tracking.',
        environment: 'Nginx Reverse Proxy, Redis Rate Limiter',
        version: 'v2.1.3',
        logs: 'WARN [rate_limiter] Failed to resolve client remote addr: header spoofing detected'
      }
    }
  ];

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      alert('Please enter at least a title and description.');
      return;
    }

    setLoading(true);
    setSubmitSuccess(null);
    try {
      const res = await analyzeIssue(formData);
      setAnalysisResult(res);
    } catch (err: any) {
      alert(err.message || 'Failed to analyze issue.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSubmit = async () => {
    if (!analysisResult) return;
    setSubmitting(true);
    try {
      const res = await createIssue(formData);
      setSubmitSuccess(`Issue #${res.id} successfully created and triaged in repository!`);
      if (onIssueCreated) onIssueCreated();
    } catch (err: any) {
      alert(err.message || 'Failed to save issue.');
    } finally {
      setSubmitting(false);
    }
  };

  const loadSample = (sample: typeof sampleInputs[0]) => {
    setFormData(sample.data);
    setAnalysisResult(null);
    setSubmitSuccess(null);
  };

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case 'Bug':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-lg">
            <Bug className="w-6 h-6 text-red-400" />
            <span>🐛 BUG</span>
          </div>
        );
      case 'Feature':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 font-bold text-lg">
            <Lightbulb className="w-6 h-6 text-blue-400" />
            <span>💡 FEATURE</span>
          </div>
        );
      case 'Question':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-lg">
            <HelpCircle className="w-6 h-6 text-emerald-400" />
            <span>❓ QUESTION</span>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header Banner */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
              DevLens Core AI Engine
            </span>
          </div>
          <h1 className="text-3xl font-extrabold theme-text-main mt-2">AI Issue Analysis & Smart Triage</h1>
          <p className="theme-text-sub text-sm mt-1">
            Submit software issue reports for natural language supervised ML classification, quality scoring, priority & team recommendation, and duplicate detection.
          </p>
        </div>

        {/* Quick Sample Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-2">
          <span className="text-xs theme-text-sub font-semibold whitespace-nowrap">Load Preset Examples:</span>
          <div className="flex flex-wrap gap-1.5">
            {sampleInputs.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadSample(sample)}
                className="text-xs px-2.5 py-1 rounded-lg theme-card-inner theme-text-main border border-slate-200 dark:border-slate-800 hover:border-indigo-500/50 hover:bg-indigo-500/10 transition cursor-pointer font-medium"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {submitSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-semibold">{submitSuccess}</span>
          </div>
          <button
            onClick={() => { setAnalysisResult(null); setSubmitSuccess(null); }}
            className="text-xs underline hover:text-emerald-500 cursor-pointer"
          >
            Analyze Another Issue
          </button>
        </div>
      )}

      {/* Main Grid: Form + Live Analysis Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Issue Input Form & File Upload */}
        <div className="lg:col-span-6 space-y-6">

          {/* File Upload Zone for PDF / ZIP / LOG */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
              }
            }}
            className={`theme-card rounded-2xl p-5 border-2 border-dashed transition-all text-center cursor-pointer ${
              isDragging ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]' : 'border-slate-300 dark:border-slate-700 hover:border-indigo-500/50'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
              accept=".pdf,.zip,.txt,.log,.json,.md"
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center space-y-2">
              <div className="p-3 rounded-full bg-indigo-500/10 text-indigo-500">
                <UploadCloud className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <p className="text-sm font-bold theme-text-main">
                  Upload PDF or ZIP Issue Attachment
                </p>
                <p className="text-xs theme-text-sub mt-0.5 max-w-md mx-auto">
                  Drag & drop or click to upload <span className="font-semibold text-indigo-500">.pdf, .zip, .log, .txt</span> files. DevLens will extract text, logs & stack traces, run ML triage, and rectify errors automatically.
                </p>
              </div>
              {selectedFile && (
                <div className="inline-flex items-center space-x-2 text-xs font-semibold px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 mt-2 border border-indigo-500/30">
                  {selectedFile.name.endsWith('.pdf') ? <FileText className="w-3.5 h-3.5 text-indigo-400" /> : <FileArchive className="w-3.5 h-3.5 text-indigo-400" />}
                  <span>{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}
            </div>
          </div>

          <form onSubmit={handleAnalyze} className="theme-card rounded-2xl p-6 space-y-5 shadow-md">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h2 className="text-lg font-bold theme-text-main flex items-center space-x-2">
                <span>Issue Details</span>
              </h2>
              <span className="text-xs theme-text-muted">* Required Title & Description</span>
            </div>

            {/* Title */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider theme-text-sub mb-1.5">
                Issue Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g. Application crashes during file upload"
                className="w-full theme-input rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider theme-text-sub mb-1.5">
                Description / Body <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={5}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Provide full description, context, or request details..."
                className="w-full theme-input rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition"
                required
              />
            </div>

            {/* Additional Optional Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider theme-text-muted mb-1">Steps to Reproduce</label>
                <textarea
                  rows={2}
                  value={formData.steps_to_reproduce}
                  onChange={(e) => setFormData({ ...formData, steps_to_reproduce: e.target.value })}
                  placeholder="1. Step 1..."
                  className="w-full theme-input rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider theme-text-muted mb-1">Expected vs Actual</label>
                <textarea
                  rows={2}
                  value={formData.expected_behavior}
                  onChange={(e) => setFormData({ ...formData, expected_behavior: e.target.value })}
                  placeholder="Expected behavior..."
                  className="w-full theme-input rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider theme-text-muted mb-1">Environment / OS</label>
                <input
                  type="text"
                  value={formData.environment}
                  onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                  placeholder="e.g. Windows 11, Chrome 120"
                  className="w-full theme-input rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider theme-text-muted mb-1">Error Logs / Traceback</label>
                <input
                  type="text"
                  value={formData.logs}
                  onChange={(e) => setFormData({ ...formData, logs: e.target.value })}
                  placeholder="e.g. NullPointerException..."
                  className="w-full theme-input rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm tracking-wide shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition cursor-pointer"
            >
              {loading ? (
                <>
                  <RotateCcw className="w-5 h-5 animate-spin" />
                  <span>Classifying & Triaging...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>ANALYZE ISSUE</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: DevLens Analysis Results Panel */}
        <div className="lg:col-span-6 space-y-6">
          {!analysisResult && !loading && (
            <div className="theme-card rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[480px]">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                <Sparkles className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold theme-text-main">Awaiting Issue Analysis</h3>
              <p className="theme-text-sub text-sm max-w-sm mt-2">
                Enter issue details on the left or choose a preset sample to view natural language ML predictions, explainability signals, quality score, and duplicate checks.
              </p>
            </div>
          )}

          {loading && (
            <div className="theme-card rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[480px]">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                <RotateCcw className="w-8 h-8 animate-spin" />
              </div>
              <h3 className="text-xl font-bold theme-text-main">Processing NLP & ML Classifier</h3>
              <p className="theme-text-sub text-sm max-w-sm mt-2">
                Executing TF-IDF transformation, Linear SVM model inference, term explainability extraction, quality scoring, and duplicate matching...
              </p>
            </div>
          )}

          {analysisResult && !loading && (
            <div className="space-y-6">
              {/* Category & Confidence Card */}
              <div className="theme-card rounded-2xl p-6 space-y-6 shadow-md">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                  <div>
                    <span className="text-xs font-semibold theme-text-sub uppercase tracking-widest">Predicted Category</span>
                    <div className="mt-2">{getCategoryBadge(analysisResult.predicted_category)}</div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-semibold theme-text-sub uppercase tracking-widest block">Confidence Score</span>
                    <span className="text-3xl font-extrabold theme-text-main">
                      {(analysisResult.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Low Confidence Warning Alert */}
                {analysisResult.is_low_confidence && (
                  <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-300 flex items-start space-x-3 text-xs">
                    <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold block">Low-Confidence Indicator Active</span>
                      <span>{analysisResult.confidence_message}</span>
                    </div>
                  </div>
                )}

                {/* Top Predictions Probabilities */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider theme-text-sub mb-3">Top 3 Class Probabilities</h4>
                  <div className="space-y-2">
                    {analysisResult.top_predictions.map((pred, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="theme-text-main">{pred.category}</span>
                          <span className="theme-text-sub font-mono">{(pred.probability * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full theme-card-inner rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              pred.category === 'Bug' ? 'bg-red-500' : pred.category === 'Feature' ? 'bg-blue-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${pred.probability * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Explainable AI (XAI) Term Signals */}
                <div className="theme-card-inner rounded-xl p-4 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 flex items-center space-x-1.5">
                    <Sparkles className="w-4 h-4" />
                    <span>Why DevLens Predicted {analysisResult.predicted_category}?</span>
                  </h4>
                  <div className="flex flex-wrap gap-1.5 py-1">
                    {analysisResult.important_signals.map((term, idx) => (
                      <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20 font-mono">
                        {term}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs theme-text-sub">{analysisResult.explanation_note}</p>

                  {/* Expandable Technical Explanation */}
                  {analysisResult.technical_explanation && (
                    <details className="pt-2 border-t border-slate-200 dark:border-slate-800/80 group">
                      <summary className="text-xs font-semibold theme-text-sub cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition flex items-center justify-between">
                        <span>Technical Explanation & Feature Weights</span>
                        <span className="text-[10px] theme-text-muted font-mono">Click to expand</span>
                      </summary>
                      <div className="mt-2 space-y-2 text-[11px] font-mono theme-text-sub theme-card p-3 rounded-lg border">
                        <div><strong className="theme-text-main">Vectorizer:</strong> {analysisResult.technical_explanation.vectorizer_type || "TF-IDF (1,2-grams)"}</div>
                        <div><strong className="theme-text-main">Vocabulary Size:</strong> {analysisResult.technical_explanation.feature_space_dim || 1014} features</div>
                        <div><strong className="theme-text-main">Active Document Terms:</strong> {analysisResult.technical_explanation.active_terms_in_doc || 12}</div>
                        {analysisResult.technical_explanation.top_weighted_features && (
                          <div className="pt-1">
                            <strong className="theme-text-main block mb-1">Top Linear Feature Weights:</strong>
                            {Object.entries(analysisResult.technical_explanation.top_weighted_features).map(([feat, w], i) => (
                              <div key={i} className="flex justify-between text-indigo-600 dark:text-indigo-300">
                                <span>{feat}</span>
                                <span>+{w}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                </div>
              </div>

              {/* Quality & Recommendations Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Quality Score Card */}
                <div className="theme-card rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider theme-text-sub">Issue Quality</h4>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded theme-card-inner theme-text-main">
                      {analysisResult.quality_grade}
                    </span>
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-3xl font-extrabold theme-text-main">{analysisResult.quality_score}</span>
                    <span className="theme-text-muted font-bold text-sm">/ 100</span>
                  </div>

                  {analysisResult.quality_suggestions.length > 0 && (
                    <div className="space-y-1 pt-2 border-t border-slate-200 dark:border-slate-800">
                      <span className="text-[11px] font-semibold theme-text-sub block">Missing Information & Checklist:</span>
                      {analysisResult.quality_suggestions.map((sugg, i) => (
                        <p key={i} className="text-[11px] text-amber-600 dark:text-amber-400 leading-tight">❌ {sugg}</p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Priority & Team Card */}
                <div className="theme-card rounded-2xl p-5 space-y-3">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider theme-text-sub block">Priority Recommendation</span>
                    <span className={`text-base font-bold ${
                      analysisResult.priority_recommendation.level === 'Critical' ? 'text-red-500' :
                      analysisResult.priority_recommendation.level === 'High' ? 'text-amber-500' : 'text-blue-500'
                    }`}>
                      {analysisResult.priority_recommendation.level} Priority
                    </span>
                    <p className="text-[11px] theme-text-sub mt-0.5">Why: {analysisResult.priority_recommendation.rationale}</p>
                  </div>

                  <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
                    <span className="text-[11px] font-bold uppercase tracking-wider theme-text-sub block">Suggested Engineering Team</span>
                    <span className="text-base font-bold text-indigo-600 dark:text-indigo-400">{analysisResult.suggested_team.name}</span>
                    <p className="text-[11px] theme-text-sub mt-0.5">Rule signal match (Confidence: {Math.round((analysisResult.suggested_team.confidence_score || 0.75) * 100)}%)</p>
                  </div>
                </div>
              </div>

              {/* Extracted File Info Badge if uploaded */}
              {analysisResult.extracted_file_info && (
                <div className="theme-card-inner rounded-xl p-4 border border-indigo-500/30 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-500">
                      {analysisResult.extracted_file_info.file_type === 'PDF' ? <FileText className="w-5 h-5 text-indigo-500" /> : <FileArchive className="w-5 h-5 text-indigo-500" />}
                    </div>
                    <div>
                      <span className="font-bold theme-text-main block">{analysisResult.extracted_file_info.filename}</span>
                      <span className="theme-text-sub text-[11px]">
                        Extracted {analysisResult.extracted_file_info.file_type} attachment • {analysisResult.extracted_file_info.logs_extracted ? 'Logs & Stacktraces Parsed' : 'Text Content Parsed'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Automated Error Rectification Card */}
              {analysisResult.error_rectification && (
                <div className="theme-card rounded-2xl p-5 space-y-4 border border-indigo-500/30 shadow-md">
                  <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 flex items-center space-x-2">
                      <Wrench className="w-4 h-4 text-indigo-500" />
                      <span>Automated Error Rectification & Resolution Guide</span>
                    </h4>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-500 uppercase">
                      DevLens AI Fix Engine
                    </span>
                  </div>

                  <div>
                    <span className="text-xs font-semibold theme-text-sub block">Identified Root Cause:</span>
                    <p className="text-sm font-bold theme-text-main mt-0.5">
                      {analysisResult.error_rectification.root_cause}
                    </p>
                  </div>

                  {analysisResult.error_rectification.rectification_steps.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-xs font-semibold theme-text-sub block">Recommended Rectification Steps:</span>
                      <ul className="space-y-1">
                        {analysisResult.error_rectification.rectification_steps.map((step, idx) => (
                          <li key={idx} className="text-xs theme-text-main flex items-start space-x-2">
                            <span className="text-indigo-500 font-bold">•</span>
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.error_rectification.recommended_code_fix && (
                    <div className="space-y-1.5 pt-2 border-t border-slate-200 dark:border-slate-800">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold theme-text-sub flex items-center space-x-1.5">
                          <Code2 className="w-3.5 h-3.5 text-indigo-500" />
                          <span>Recommended Code Fix Snippet:</span>
                        </span>
                      </div>
                      <pre className="p-3 rounded-xl bg-slate-950 text-indigo-300 font-mono text-[11px] overflow-x-auto border border-slate-800 leading-relaxed">
                        {analysisResult.error_rectification.recommended_code_fix}
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Duplicate Detection Alert */}
              <div className="theme-card rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider theme-text-sub flex items-center space-x-2">
                    <CopyCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <span>Duplicate Detection</span>
                  </h4>
                  <span className="text-xs theme-text-sub font-mono">
                    Max similarity: {analysisResult.duplicate_check.max_similarity_percentage}%
                  </span>
                </div>

                {analysisResult.duplicate_check.has_duplicate ? (
                  <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-300 text-xs space-y-1">
                    <span className="font-bold block">Potential Duplicate Issue Detected!</span>
                    {analysisResult.duplicate_check.potential_duplicates.slice(0, 1).map((dup, i) => (
                      <p key={i}>Similar issue #{dup.issue_id}: "{dup.title}" ({dup.similarity_percentage}% match)</p>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-xl">
                    ✓ No strong duplicate matches found in stored repository issues.
                  </p>
                )}
              </div>

              {/* Model Version Tag */}
              <div className="flex items-center justify-between text-xs theme-text-muted px-1">
                <span>Model: <strong className="theme-text-main">{analysisResult.model_name}</strong> ({analysisResult.model_version})</span>
                <button
                  type="button"
                  onClick={() => setAnalysisResult(null)}
                  className="text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer"
                >
                  Reset Analysis
                </button>
              </div>

              {/* Submit / Confirm Action Buttons */}
              <div className="flex items-center space-x-3 pt-2">
                <button
                  type="button"
                  onClick={handleConfirmSubmit}
                  disabled={submitting}
                  className="flex-1 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm tracking-wide shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition cursor-pointer"
                >
                  {submitting ? (
                    <RotateCcw className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>CONFIRM & SUBMIT ISSUE</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

