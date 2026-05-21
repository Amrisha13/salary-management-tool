import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Edit2 } from 'lucide-react';
import { employeeAPI } from '../api';
import './EmployeeManager.css';

const EmployeeManager = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [perPage] = useState(20);
  const [filters, setFilters] = useState({ country: '', jobTitle: '' });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    first_name: '',
    last_name: '',
    job_title: '',
    country: '',
    salary: '',
    department: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    fetchEmployees();
  }, [page, filters]);

  const fetchEmployees = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await employeeAPI.getAll(page, perPage, filters);
      setEmployees(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      setError('Failed to fetch employees');
      console.error(err);
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (editingId) {
        await employeeAPI.update(editingId, formData);
      } else {
        await employeeAPI.create(formData);
      }
      
      setShowForm(false);
      setEditingId(null);
      setFormData({
        full_name: '',
        first_name: '',
        last_name: '',
        job_title: '',
        country: '',
        salary: '',
        department: '',
        email: '',
        phone: '',
      });
      setPage(1);
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save employee');
    }
  };

  const handleEdit = (employee) => {
    setEditingId(employee.id);
    setFormData({
      full_name: employee.full_name,
      first_name: employee.first_name,
      last_name: employee.last_name,
      job_title: employee.job_title,
      country: employee.country,
      salary: employee.salary,
      department: employee.department || '',
      email: employee.email,
      phone: employee.phone || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await employeeAPI.delete(id);
        fetchEmployees();
      } catch (err) {
        setError('Failed to delete employee');
        console.error(err);
      }
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value,
    }));
    setPage(1);
  };

  const pages = Math.ceil(total / perPage);

  return (
    <div className="employee-manager">
      <h2>Employee Management</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="toolbar">
        <button 
          className="btn btn-primary"
          onClick={() => {
            setShowForm(!showForm);
            if (showForm) setEditingId(null);
          }}
        >
          <Plus size={20} />
          {showForm && !editingId ? 'Cancel' : 'Add Employee'}
        </button>

        <div className="filters">
          <input
            type="text"
            placeholder="Filter by country"
            name="country"
            value={filters.country}
            onChange={handleFilterChange}
            className="input"
          />
          <input
            type="text"
            placeholder="Filter by job title"
            name="jobTitle"
            value={filters.jobTitle}
            onChange={handleFilterChange}
            className="input"
          />
        </div>
      </div>

      {showForm && (
        <form className="employee-form" onSubmit={handleSubmit}>
          <h3>{editingId ? 'Edit Employee' : 'Add New Employee'}</h3>
          
          <div className="form-grid">
            <input
              type="text"
              name="full_name"
              placeholder="Full Name"
              value={formData.full_name}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="text"
              name="first_name"
              placeholder="First Name"
              value={formData.first_name}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="text"
              name="last_name"
              placeholder="Last Name"
              value={formData.last_name}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="text"
              name="job_title"
              placeholder="Job Title"
              value={formData.job_title}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="text"
              name="country"
              placeholder="Country"
              value={formData.country}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="number"
              name="salary"
              placeholder="Salary"
              value={formData.salary}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="text"
              name="department"
              placeholder="Department"
              value={formData.department}
              onChange={handleFormChange}
              className="input"
            />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleFormChange}
              required
              className="input"
            />
            <input
              type="tel"
              name="phone"
              placeholder="Phone"
              value={formData.phone}
              onChange={handleFormChange}
              className="input"
            />
          </div>

          <button type="submit" className="btn btn-success">
            {editingId ? 'Update' : 'Create'} Employee
          </button>
        </form>
      )}

      <div className="employees-table-container">
        {loading ? (
          <div className="loading">Loading employees...</div>
        ) : employees.length === 0 ? (
          <div className="empty-state">No employees found</div>
        ) : (
          <>
            <table className="employees-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Job Title</th>
                  <th>Country</th>
                  <th>Salary</th>
                  <th>Department</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp.id}>
                    <td>{emp.full_name}</td>
                    <td>{emp.job_title}</td>
                    <td>{emp.country}</td>
                    <td>${emp.salary.toLocaleString()}</td>
                    <td>{emp.department || '-'}</td>
                    <td>{emp.email}</td>
                    <td>
                      <button
                        className="btn-icon"
                        onClick={() => handleEdit(emp)}
                        title="Edit"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        className="btn-icon danger"
                        onClick={() => handleDelete(emp.id)}
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pagination">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn"
              >
                Previous
              </button>
              <span>Page {page} of {pages}</span>
              <button
                onClick={() => setPage(Math.min(pages, page + 1))}
                disabled={page === pages}
                className="btn"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EmployeeManager;
