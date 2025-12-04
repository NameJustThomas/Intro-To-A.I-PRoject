import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState('2025-11');
  const [storeId, setStoreId] = useState('');

  const fetchAttendanceData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { month };
      if (storeId) {
        params.store_id = storeId;
      }
      const response = await axios.get(`${API_BASE_URL}/v1/dashboard/attendance-month`, { params });
      setAttendanceData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch attendance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendanceData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Attendance Dashboard</h1>
      </header>
      <main className="App-main">
        <div className="filters">
          <label>
            Month (YYYY-MM):
            <input
              type="text"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              pattern="\d{4}-\d{2}"
              placeholder="2025-11"
            />
          </label>
          <label>
            Store ID (optional):
            <input
              type="text"
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              placeholder="Store ID"
            />
          </label>
          <button onClick={fetchAttendanceData}>Load Data</button>
        </div>

        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">Error: {error}</div>}

        {attendanceData && (
          <div className="attendance-summary">
            <h2>Monthly Attendance Summary</h2>
            <div className="summary-stats">
              <p><strong>Month:</strong> {attendanceData.month}</p>
              <p><strong>Total Employees:</strong> {attendanceData.total_employees}</p>
              <p><strong>Total Check-ins:</strong> {attendanceData.total_check_ins}</p>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Present Days</th>
                  <th>Total Days</th>
                  <th>Attendance %</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.attendance_summary.map((emp, idx) => (
                  <tr key={idx}>
                    <td>{emp.employee_id}</td>
                    <td>{emp.employee_name}</td>
                    <td>{emp.present_days}</td>
                    <td>{emp.total_days}</td>
                    <td>{((emp.present_days / emp.total_days) * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

