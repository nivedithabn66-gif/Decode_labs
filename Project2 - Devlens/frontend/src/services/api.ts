import type {
  IssueAnalyzeRequest, IssueAnalyzeResponse,
  IssueRecord, DashboardStats, ModelMetadata, ErrorSample
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export async function analyzeIssue(data: IssueAnalyzeRequest): Promise<IssueAnalyzeResponse> {
  const res = await fetch(`${API_BASE}/issues/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Analysis failed: ${res.statusText}`);
  return res.json();
}

export async function analyzeFileIssue(file: File): Promise<IssueAnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/issues/analyze-file`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`File analysis failed: ${res.statusText}`);
  return res.json();
}

export async function createIssue(data: IssueAnalyzeRequest & { confirmed_category?: string }): Promise<IssueRecord> {
  const res = await fetch(`${API_BASE}/issues`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Issue creation failed: ${res.statusText}`);
  return res.json();
}

export async function fetchIssues(category?: string, status?: string, isLowConf?: boolean): Promise<IssueRecord[]> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (status) params.append('status', status);
  if (isLowConf !== undefined) params.append('is_low_conf', String(isLowConf));

  const res = await fetch(`${API_BASE}/issues?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to load issues: ${res.statusText}`);
  return res.json();
}

export async function fetchIssueDetails(id: number): Promise<IssueRecord> {
  const res = await fetch(`${API_BASE}/issues/${id}`);
  if (!res.ok) throw new Error(`Failed to load issue #${id}`);
  return res.json();
}

export async function submitFeedback(issueId: number, originalPred: string, correctedLabel: string, comment?: string) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      issue_id: issueId,
      original_prediction: originalPred,
      corrected_label: correctedLabel,
      comment: comment || ''
    }),
  });
  if (!res.ok) throw new Error(`Feedback submission failed`);
  return res.json();
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error(`Failed to load dashboard stats`);
  return res.json();
}

export async function fetchModelInfo(): Promise<ModelMetadata> {
  const res = await fetch(`${API_BASE}/model/info`);
  if (!res.ok) throw new Error(`Failed to load model info`);
  return res.json();
}

export async function fetchModelMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/model/metrics`);
  if (!res.ok) throw new Error(`Failed to load model metrics`);
  return res.json();
}

export async function fetchErrorSamples(): Promise<ErrorSample[]> {
  const res = await fetch(`${API_BASE}/model/errors`);
  if (!res.ok) throw new Error(`Failed to load error samples`);
  return res.json();
}

export async function compareIssues(titleA: string, descA: string, titleB: string, descB: string): Promise<import('../types').IssueCompareResponse> {
  const res = await fetch(`${API_BASE}/issues/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title_a: titleA,
      description_a: descA,
      title_b: titleB,
      description_b: descB,
    }),
  });
  if (!res.ok) throw new Error(`Comparison request failed`);
  return res.json();
}

export async function fetchModelHealth(): Promise<import('../types').ModelHealth> {
  const res = await fetch(`${API_BASE}/model/health`);
  if (!res.ok) throw new Error(`Failed to load model health`);
  return res.json();
}

export async function fetchModelRegistry(): Promise<{ active_version: string; total_versions: number; registry: import('../types').ModelRegistryItem[] }> {
  const res = await fetch(`${API_BASE}/model/registry`);
  if (!res.ok) throw new Error(`Failed to load model registry`);
  return res.json();
}

export async function fetchDistributionShift(): Promise<import('../types').DistributionShift> {
  const res = await fetch(`${API_BASE}/model/distribution-shift`);
  if (!res.ok) throw new Error(`Failed to load distribution shift`);
  return res.json();
}

export async function fetchSystemHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Failed to load system health`);
  return res.json();
}

