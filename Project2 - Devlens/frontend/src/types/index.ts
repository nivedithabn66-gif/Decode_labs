export type IssueCategory = 'Bug' | 'Feature' | 'Question';

export interface TopPrediction {
  category: IssueCategory;
  probability: number;
}

export interface DuplicateMatch {
  issue_id: number;
  title: string;
  category: IssueCategory;
  similarity: number;
  similarity_percentage: number;
  created_at: string;
  status: string;
}

export interface IssueAnalyzeRequest {
  title: string;
  description: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
  version?: string;
  logs?: string;
}

export interface IssueAnalyzeResponse {
  title: string;
  predicted_category: IssueCategory;
  confidence: number;
  confidence_level?: 'HIGH' | 'MEDIUM' | 'LOW';
  top_predictions: TopPrediction[];
  is_low_confidence: boolean;
  confidence_message: string;
  important_signals: string[];
  explanation_note: string;
  technical_explanation?: {
    vectorizer_type?: string;
    feature_space_dim?: number;
    active_terms_in_doc?: number;
    top_weighted_features?: Record<string, number>;
  };
  quality_score: number;
  quality_grade: string;
  quality_breakdown: Record<string, number>;
  quality_suggestions: string[];
  priority_recommendation: {
    level: 'Low' | 'Medium' | 'High' | 'Critical';
    type: string;
    rationale: string;
  };
  suggested_team: {
    name: string;
    type: string;
    confidence_score: number;
  };
  duplicate_check: {
    has_duplicate: boolean;
    max_similarity: number;
    max_similarity_percentage: number;
    potential_duplicates: DuplicateMatch[];
    total_matches_found: number;
  };
  model_name: string;
  model_version: string;
  extracted_file_info?: {
    filename: string;
    file_type: string;
    extracted_files: string[];
    description_snippet: string;
    logs_extracted: boolean;
  };
  error_rectification?: {
    root_cause: string;
    rectification_steps: string[];
    recommended_code_fix?: string | null;
  };
}

export interface IssueRecord {
  id: number;
  title: string;
  description: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
  version?: string;
  logs?: string;
  predicted_category: IssueCategory;
  confidence: number;
  is_low_confidence: boolean;
  quality_score: number;
  priority_recommendation: string;
  team_recommendation: string;
  model_version: string;
  status: string;
  created_at: string;
}

export interface DashboardStats {
  total_issues: number;
  bugs: number;
  features: number;
  questions: number;
  low_confidence_count: number;
  low_confidence_rate: number;
  avg_quality_score: number;
  current_model: string;
  model_version: string;
  macro_f1: number;
  category_distribution: {
    category: string;
    count: number;
    color: string;
  }[];
}

export interface ModelMetadata {
  model_name: string;
  version: string;
  training_timestamp: string;
  primary_metric: string;
  best_macro_f1: number;
  best_accuracy: number;
  dataset_source: string;
  train_samples: number;
  test_samples: number;
  num_features: number;
  label_classes: string[];
  candidate_comparisons: {
    model_name: string;
    accuracy: number;
    macro_precision: number;
    macro_recall: number;
    macro_f1: number;
    weighted_f1: number;
    train_time_sec: number;
    pred_latency_ms: number;
  }[];
}

export interface ErrorSample {
  id: number;
  title: string;
  text_snippet: string;
  actual: string;
  predicted: string;
  confidence: number;
  is_correct: boolean;
}

export interface IssueCompareResponse {
  similarity_score: number;
  similarity_percentage: number;
  common_terms: string[];
  category_match: boolean;
  category_a: string;
  category_b: string;
  comparison_summary: string;
}

export interface ModelHealth {
  current_model: string;
  model_version: string;
  dataset_version: string;
  macro_f1: number;
  accuracy: number;
  training_date: string;
  total_predictions: number;
  low_confidence_count: number;
  low_confidence_rate: number;
  model_status: string;
  status_code: string;
}

export interface ModelRegistryItem {
  version: string;
  model_name: string;
  dataset: string;
  macro_f1: number;
  accuracy: number;
  training_date: string;
  status: string;
  is_active: boolean;
}

export interface DistributionShift {
  training_distribution: Record<string, number>;
  production_distribution: Record<string, number>;
  has_data_shift: boolean;
  shift_warning: string;
}

