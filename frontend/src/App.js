import React, { useState } from 'react';
import EmployeeManager from './components/EmployeeManager';
import SalaryInsights from './components/SalaryInsights';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('employees');

  return (
    <div className="app">
      <header className="app-header">
        <h1>💼 Salary Management Tool</h1>
        <p>HR Management System for 10,000+ Employees</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'employees' ? 'active' : ''}`}
          onClick={() => setActiveTab('employees')}
        >
          👥 Employees
        </button>
        <button
          className={`nav-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          📊 Salary Insights
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'employees' && <EmployeeManager />}
        {activeTab === 'insights' && <SalaryInsights />}
      </main>

      <footer className="app-footer">
        <p>© 2026 Salary Management Tool. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
