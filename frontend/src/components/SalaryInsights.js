import React, { useState, useEffect } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { insightsAPI } from '../api';
import './SalaryInsights.css';

const SalaryInsights = () => {
  const [summary, setSummary] = useState(null);
  const [countries, setCountries] = useState([]);
  const [jobTitles, setJobTitles] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [countryDetail, setCountryDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

  useEffect(() => {
    fetchSummary();
    fetchCountries();
  }, []);

  useEffect(() => {
    if (selectedCountry) {
      fetchCountryDetail();
      fetchJobTitles();
    }
  }, [selectedCountry]);

  const fetchSummary = async () => {
    try {
      const response = await insightsAPI.getCountrySummary();
      setSummary(response.data);
    } catch (err) {
      console.error('Failed to fetch summary', err);
    }
  };

  const fetchCountries = async () => {
    try {
      const response = await insightsAPI.getAllCountries();
      setCountries(response.data);
    } catch (err) {
      console.error('Failed to fetch countries', err);
    }
  };

  const fetchCountryDetail = async () => {
    setLoading(true);
    try {
      const response = await insightsAPI.getCountryInsights(selectedCountry);
      setCountryDetail(response.data);
    } catch (err) {
      console.error('Failed to fetch country detail', err);
    }
    setLoading(false);
  };

  const fetchJobTitles = async () => {
    try {
      const response = await insightsAPI.getAllJobTitles(selectedCountry);
      setJobTitles(response.data);
    } catch (err) {
      console.error('Failed to fetch job titles', err);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="salary-insights">
      <h2>Salary Insights & Analytics</h2>

      {error && <div className="error-message">{error}</div>}

      {summary && (
        <div className="summary-grid">
          <div className="stat-card">
            <div className="stat-label">Total Employees</div>
            <div className="stat-value">{summary.total_employees.toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Average Salary</div>
            <div className="stat-value">{formatCurrency(summary.average_salary)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Min Salary</div>
            <div className="stat-value">{formatCurrency(summary.min_salary)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Max Salary</div>
            <div className="stat-value">{formatCurrency(summary.max_salary)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Countries</div>
            <div className="stat-value">{summary.countries}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Job Titles</div>
            <div className="stat-value">{summary.job_titles}</div>
          </div>
        </div>
      )}

      <div className="charts-section">
        <div className="chart-container">
          <h3>Employees by Country</h3>
          {countries.length > 0 && (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={countries}
                  dataKey="employee_count"
                  nameKey="country"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {countries.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => value.toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="chart-container">
          <h3>Average Salary by Country</h3>
          {countries.length > 0 && (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={countries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="average_salary" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="country-detail-section">
        <h3>Country Analysis</h3>
        <select
          value={selectedCountry}
          onChange={(e) => setSelectedCountry(e.target.value)}
          className="select"
        >
          <option value="">Select a country...</option>
          {countries.map(c => (
            <option key={c.country} value={c.country}>
              {c.country}
            </option>
          ))}
        </select>

        {loading && <div className="loading">Loading...</div>}

        {selectedCountry && countryDetail && (
          <div className="detail-grid">
            <div className="detail-card">
              <div className="detail-label">Country</div>
              <div className="detail-value">{countryDetail.country}</div>
            </div>
            <div className="detail-card">
              <div className="detail-label">Total Employees</div>
              <div className="detail-value">{countryDetail.total_employees}</div>
            </div>
            <div className="detail-card">
              <div className="detail-label">Average Salary</div>
              <div className="detail-value">{formatCurrency(countryDetail.average_salary)}</div>
            </div>
            <div className="detail-card">
              <div className="detail-label">Min Salary</div>
              <div className="detail-value">{formatCurrency(countryDetail.min_salary)}</div>
            </div>
            <div className="detail-card">
              <div className="detail-label">Max Salary</div>
              <div className="detail-value">{formatCurrency(countryDetail.max_salary)}</div>
            </div>
            <div className="detail-card">
              <div className="detail-label">Median Salary</div>
              <div className="detail-value">{formatCurrency(countryDetail.median_salary)}</div>
            </div>

            {jobTitles.length > 0 && (
              <div className="job-titles-section">
                <h4>Job Titles in {selectedCountry}</h4>
                <div className="job-titles-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Job Title</th>
                        <th>Count</th>
                        <th>Avg Salary</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobTitles.slice(0, 10).map((job, idx) => (
                        <tr key={idx}>
                          <td>{job.job_title}</td>
                          <td>{job.employee_count}</td>
                          <td>{formatCurrency(job.average_salary)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SalaryInsights;
