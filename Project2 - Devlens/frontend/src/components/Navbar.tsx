import React from 'react';
import {
  LayoutDashboard, SearchCode, ListFilter, CopyCheck,
  BarChart3, AlertOctagon, Settings, Cpu, Sun, Moon
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentModel?: string;
  modelVersion?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, currentModel = "Linear SVM", modelVersion = "v1.0.0" }) => {
  const { setTheme, isDark } = useTheme();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analyze', label: 'Analyze Issue', icon: SearchCode },
    { id: 'issues', label: 'Issues Queue', icon: ListFilter },
    { id: 'duplicates', label: 'Duplicate Check', icon: CopyCheck },
    { id: 'performance', label: 'Model Metrics', icon: BarChart3 },
    { id: 'error-analysis', label: 'Error Workbench', icon: AlertOctagon },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="theme-nav sticky top-0 z-50 shadow-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight theme-text-main">DevLens</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-500 dark:text-indigo-400 font-semibold border border-indigo-500/20">
                  ML Triage
                </span>
              </div>
              <span className="text-[10px] theme-text-muted font-medium block">DecodeLabs AI Project 2</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30 font-bold'
                      : 'theme-text-sub hover:bg-slate-200/50 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'theme-text-muted'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Active Deployed Model Badge & Theme Toggle */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setTheme(isDark ? 'light' : 'dark')}
              className="p-2 rounded-lg theme-card-inner theme-text-sub hover:theme-text-main transition-colors cursor-pointer"
              title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
            </button>

            <div className="hidden lg:flex items-center space-x-2 theme-card-inner rounded-lg px-3 py-1.5 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="theme-text-muted">Deployed Model:</span>
              <span className="theme-text-main font-semibold">{currentModel}</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-mono bg-indigo-500/10 px-1.5 py-0.5 rounded text-[11px]">{modelVersion}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};


