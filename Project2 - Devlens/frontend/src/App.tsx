import { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { AnalyzeIssuePage } from './pages/AnalyzeIssuePage';
import { IssuesPage } from './pages/IssuesPage';
import { IssueDetailsPage } from './pages/IssueDetailsPage';
import { DuplicateDetectionPage } from './pages/DuplicateDetectionPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { ErrorAnalysisPage } from './pages/ErrorAnalysisPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('analyze');
  const [selectedIssueId, setSelectedIssueId] = useState<number | null>(null);

  const handleSelectIssue = (id: number) => {
    setSelectedIssueId(id);
    setActiveTab('issue-details');
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage setActiveTab={setActiveTab} />;
      case 'analyze':
        return <AnalyzeIssuePage onIssueCreated={() => setActiveTab('issues')} />;
      case 'issues':
        return <IssuesPage onSelectIssue={handleSelectIssue} />;
      case 'issue-details':
        return selectedIssueId ? (
          <IssueDetailsPage issueId={selectedIssueId} onBack={() => setActiveTab('issues')} />
        ) : (
          <IssuesPage onSelectIssue={handleSelectIssue} />
        );
      case 'duplicates':
        return <DuplicateDetectionPage />;
      case 'performance':
        return <ModelPerformancePage />;
      case 'error-analysis':
        return <ErrorAnalysisPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <AnalyzeIssuePage onIssueCreated={() => setActiveTab('issues')} />;
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen app-bg flex flex-col font-sans transition-colors duration-200">
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} currentModel="Linear SVM" modelVersion="v1.0.0" />
        <main className="flex-1 pb-16">{renderActivePage()}</main>
        
        <footer className="theme-card border-t py-4 text-center text-xs theme-text-muted">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>DevLens AI Platform — DecodeLabs Artificial Intelligence Project 2</span>
            <span>Supervised ML Issue Classifier (TF-IDF + Linear SVM)</span>
          </div>
        </footer>
      </div>
    </ThemeProvider>

  );
}

export default App;

