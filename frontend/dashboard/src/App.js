import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authEmployee, setAuthEmployee] = useState(null);
  
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' or 'register'
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState('2025-11');
  const [storeId, setStoreId] = useState('');
  
  // Face registration state
  const [employeeId, setEmployeeId] = useState('');
  const [selectedImages, setSelectedImages] = useState([]);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState(null);
  const [registerSuccess, setRegisterSuccess] = useState(null);
  const [availableEmployees, setAvailableEmployees] = useState([]);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const employeeId = localStorage.getItem('auth_employee_id');
      const employeeName = localStorage.getItem('auth_employee_name');
      const authTimestamp = localStorage.getItem('auth_timestamp');
      
      console.log('Dashboard auth check:', { employeeId, employeeName, authTimestamp });
      
      if (employeeId && employeeName && authTimestamp) {
        // Check if session is still valid (e.g., within 8 hours)
        const timestamp = new Date(authTimestamp);
        const now = new Date();
        const hoursDiff = (now - timestamp) / (1000 * 60 * 60);
        
        console.log('Session age:', hoursDiff, 'hours');
        
        if (hoursDiff < 8) {
          setIsAuthenticated(true);
          setAuthEmployee({
            id: employeeId,
            name: employeeName,
            timestamp: authTimestamp
          });
          console.log('Authentication successful');
        } else {
          // Session expired
          console.log('Session expired');
          localStorage.removeItem('auth_employee_id');
          localStorage.removeItem('auth_employee_name');
          localStorage.removeItem('auth_timestamp');
        }
      } else {
        console.log('No authentication found in localStorage');
      }
    };
    
    checkAuth();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_employee_id');
    localStorage.removeItem('auth_employee_name');
    localStorage.removeItem('auth_timestamp');
    setIsAuthenticated(false);
    setAuthEmployee(null);
  };

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

  const fetchAvailableEmployees = async () => {
    try {
      // Get employees from attendance data if available
      if (attendanceData && attendanceData.attendance_summary) {
        const employees = attendanceData.attendance_summary.map(emp => ({
          id: emp.employee_id,
          name: emp.employee_name
        }));
        setAvailableEmployees(employees);
      } else {
        // Fallback: Use sample employee IDs
        setAvailableEmployees([
          { id: 'E001', name: 'Nguyen Van A' },
          { id: 'E002', name: 'Tran Thi B' }
        ]);
      }
    } catch (err) {
      // Fallback to sample IDs
      setAvailableEmployees([
        { id: 'E001', name: 'Nguyen Van A' },
        { id: 'E002', name: 'Tran Thi B' }
      ]);
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchAttendanceData();
    } else if (activeTab === 'register') {
      fetchAvailableEmployees();
    }
  }, [activeTab, attendanceData]);

  const handleImageSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedImages(files);
    setRegisterError(null);
    setRegisterSuccess(null);
  };

  const handleFaceRegistration = async () => {
    if (!employeeId.trim()) {
      setRegisterError('Please enter Employee ID');
      return;
    }

    if (selectedImages.length === 0) {
      setRegisterError('Please select at least one image');
      return;
    }

    if (selectedImages.length < 2) {
      setRegisterError('Please select at least 2-3 images for better accuracy');
      return;
    }

    setRegisterLoading(true);
    setRegisterError(null);
    setRegisterSuccess(null);

    try {
      const formData = new FormData();
      formData.append('employee_id', employeeId.trim());
      selectedImages.forEach((image) => {
        formData.append('images', image);
      });

      const response = await axios.post(
        `${API_BASE_URL}/v1/employee/register-face`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setRegisterSuccess(response.data);
      setSelectedImages([]);
      setEmployeeId('');
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = '';
    } catch (err) {
      setRegisterError(
        err.response?.data?.detail || 
        err.response?.data?.message || 
        'Failed to register face. Please try again.'
      );
    } finally {
      setRegisterLoading(false);
    }
  };

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="App">
        <div className="login-prompt">
          <div className="login-prompt-content">
            <h1>🔒 Authentication Required</h1>
            <p>Please check in at the kiosk to access the dashboard.</p>
            <p className="login-instructions">
              Go to the <strong>Check-in Kiosk</strong> and use face recognition to check in.
              After successful check-in, you will be automatically redirected here.
            </p>
            <div className="login-actions">
              <a href="http://localhost:3001" className="btn btn-primary">
                Go to Check-in Kiosk
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>AI Attendance Dashboard</h1>
          <div className="user-info">
            <span className="welcome-text">
              Welcome, <strong>{authEmployee?.name}</strong> ({authEmployee?.id})
            </span>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Attendance Reports
          </button>
          <button 
            className={activeTab === 'register' ? 'active' : ''}
            onClick={() => setActiveTab('register')}
          >
            Register Face
          </button>
        </nav>
      </header>
      <main className="App-main">
        {activeTab === 'register' ? (
          <div className="face-registration">
            <h2>Register Employee Face</h2>
            <p className="instruction-text">
              Upload 2-3 clear photos of the employee's face for face recognition.
              Use front-facing photos with good lighting for best results.
            </p>

            <div className="registration-form">
              <div className="form-group">
                <label htmlFor="employee-id">Employee ID:</label>
                <input
                  id="employee-id"
                  type="text"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  placeholder="Enter Employee ID (e.g., E001)"
                  disabled={registerLoading}
                  list="employee-list"
                />
                <datalist id="employee-list">
                  {availableEmployees.map((emp, idx) => (
                    <option key={idx} value={emp.id}>
                      {emp.name}
                    </option>
                  ))}
                </datalist>
                <small>
                  Available employees: {availableEmployees.map(e => e.id).join(', ')} 
                  {availableEmployees.length === 0 && '(E001, E002 from sample data)'}
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="face-images">Face Images (2-3 images recommended):</label>
                <input
                  id="face-images"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageSelect}
                  disabled={registerLoading}
                />
                {selectedImages.length > 0 && (
                  <div className="image-preview-list">
                    <p><strong>Selected {selectedImages.length} image(s):</strong></p>
                    <ul>
                      {selectedImages.map((img, idx) => (
                        <li key={idx}>{img.name}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <button
                className="register-button"
                onClick={handleFaceRegistration}
                disabled={registerLoading || !employeeId.trim() || selectedImages.length === 0}
              >
                {registerLoading ? 'Registering...' : 'Register Face'}
              </button>

              {registerError && (
                <div className="error-message">
                  <strong>Error:</strong> {registerError}
                </div>
              )}

              {registerSuccess && (
                <div className="success-message">
                  <strong>Success!</strong>
                  <p>{registerSuccess.message}</p>
                  <p>Employee ID: {registerSuccess.employee_id}</p>
                  <p>Embeddings stored: {registerSuccess.embeddings_count}</p>
                </div>
              )}
            </div>

            <div className="registration-tips">
              <h3>Tips for Best Results:</h3>
              <ul>
                <li>Use clear, front-facing photos</li>
                <li>Ensure good lighting</li>
                <li>Upload 2-3 images from different angles</li>
                <li>Avoid sunglasses, masks, or heavy makeup</li>
                <li>Make sure the face is clearly visible</li>
              </ul>
            </div>
          </div>
        ) : (
          <>
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
          </>
        )}
      </main>
    </div>
  );
}

export default App;

