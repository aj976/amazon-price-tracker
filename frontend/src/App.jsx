import React from 'react';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-bg flex flex-col items-center py-10 px-4">
      <header className="w-full max-w-5xl mb-8 flex items-center justify-between border-b border-surface pb-4">
        <div>
          <h1 className="text-3xl font-sans font-bold text-accent tracking-tighter uppercase flex items-center gap-2">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="w-8 h-8"
            >
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            APT
          </h1>
          <p className="text-textSecondary text-sm font-sans tracking-wide mt-1">
            Amazon Price Tracker
          </p>
        </div>
      </header>
      
      <main className="w-full max-w-5xl flex-1 flex flex-col gap-6">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
