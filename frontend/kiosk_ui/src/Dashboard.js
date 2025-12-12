import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = '/api';

// Employee Edit Form Component
function EmployeeEditForm({ employee, onSave, onCancel }) {
  const [empCode, setEmpCode] = useState(employee.emp_code);
  const [name, setName] = useState(employee.name);
  const [role, setRole] = useState(employee.role);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({ emp_code: empCode, name, role });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="edit-form">
      <div className="form-group">
        <label>Employee ID:</label>
        <input
          type="text"
          value={empCode}
          onChange={(e) => setEmpCode(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>Name:</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>Role:</label>
        <select value={role || 'employee'} onChange={(e) => setRole(e.target.value)} required>
          <option value="employee">Employee</option>
          <option value="manager">Manager</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn-save" disabled={saving}>
          {saving ? 'Saving...' : '💾 Save'}
        </button>
        <button type="button" className="btn-cancel" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}

// Store Edit Form Component
function StoreEditForm({ store, onSave, onCancel }) {
  const [name, setName] = useState(store.name || '');
  const [address, setAddress] = useState(store.address || '');
  const [latitude, setLatitude] = useState(store.latitude?.toString() || '');
  const [longitude, setLongitude] = useState(store.longitude?.toString() || '');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({
        name: name || null,
        address: address || null,
        latitude: latitude ? parseFloat(latitude) : null,
        longitude: longitude ? parseFloat(longitude) : null,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="edit-form">
      <div className="form-group">
        <label>Store Name:</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Address:</label>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Latitude:</label>
        <input
          type="number"
          step="any"
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
          placeholder="e.g., 10.762622"
        />
      </div>
      <div className="form-group">
        <label>Longitude:</label>
        <input
          type="number"
          step="any"
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
          placeholder="e.g., 106.660172"
        />
      </div>
      <div className="form-actions">
        <button type="submit" className="btn-save" disabled={saving}>
          {saving ? 'Saving...' : '💾 Save'}
        </button>
        <button type="button" className="btn-cancel" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}

function Dashboard() {
  const navigate = useNavigate();
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authEmployee, setAuthEmployee] = useState(null);
  const [isManagerOrAdmin, setIsManagerOrAdmin] = useState(false);
  
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'register', 'history', or 'manage'
  const [attendanceData, setAttendanceData] = useState(null);
  const [checkInHistory, setCheckInHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7)); // Current month YYYY-MM
  const [storeId, setStoreId] = useState('');
  
  // Face registration state
  const [employeeId, setEmployeeId] = useState('');
  const [selectedImages, setSelectedImages] = useState([]);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState(null);
  const [registerSuccess, setRegisterSuccess] = useState(null);
  const [availableEmployees, setAvailableEmployees] = useState([]);
  
  // Management state (for manager/admin)
  const [employees, setEmployees] = useState([]);
  const [stores, setStores] = useState([]);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [editingStore, setEditingStore] = useState(null);
  const [editingFaceEmployee, setEditingFaceEmployee] = useState(null);
  const [faceImages, setFaceImages] = useState([]);
  const [faceRegLoading, setFaceRegLoading] = useState(false);
  const [faceRegError, setFaceRegError] = useState(null);
  const [faceRegSuccess, setFaceRegSuccess] = useState(null);
  const [faceCameraStream, setFaceCameraStream] = useState(null);
  const [faceCameraMode, setFaceCameraMode] = useState(false);
  const [manageLoading, setManageLoading] = useState(false);
  const [manageError, setManageError] = useState(null);
  
  // Schedule management state
  const [scheduleStoreId, setScheduleStoreId] = useState(1);
  const [scheduleDate, setScheduleDate] = useState(new Date().toISOString().split('T')[0]);
  const [schedulesByStore, setSchedulesByStore] = useState(null);
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduleError, setScheduleError] = useState(null);
  const [editingScheduleCell, setEditingScheduleCell] = useState(null); // {storeId, date, shift}
  const [newEmployeeId, setNewEmployeeId] = useState('');
  
  // Refs for camera
  const faceVideoRef = useRef(null);
  const faceCanvasRef = useRef(null);

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
          const employeeRole = localStorage.getItem('auth_employee_role') || '';
          const role = employeeRole.toLowerCase();
          const hasAdminAccess = role === 'manager' || role === 'admin';
          
          setIsAuthenticated(true);
          setIsManagerOrAdmin(hasAdminAccess);
          setAuthEmployee({
            id: employeeId,
            name: employeeName,
            role: employeeRole,
            timestamp: authTimestamp
          });
          console.log('Authentication successful. Role:', employeeRole, 'Has admin access:', hasAdminAccess);
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
    // Redirect to check-in page
    navigate('/', { replace: true });
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
      console.error('Error fetching attendance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCheckInHistory = async () => {
    setHistoryLoading(true);
    try {
      const params = {};
      if (authEmployee?.id) {
        params.employee_id = authEmployee.id;
      }
      const response = await axios.get(`${API_BASE_URL}/v1/attendance/history`, { params });
      setCheckInHistory(response.data);
    } catch (err) {
      console.error('Error fetching check-in history:', err);
    } finally {
      setHistoryLoading(false);
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

  const fetchEmployees = async () => {
    setManageLoading(true);
    setManageError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/v1/employee`);
      setEmployees(response.data);
    } catch (err) {
      setManageError(err.response?.data?.detail || 'Failed to fetch employees');
    } finally {
      setManageLoading(false);
    }
  };

  const fetchStores = async () => {
    setManageLoading(true);
    setManageError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/v1/stores`);
      console.log('Stores response:', response.data);
      setStores(response.data || []);
    } catch (err) {
      console.error('Error fetching stores:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch stores';
      setManageError(errorMsg);
      console.error('Store fetch error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
    } finally {
      setManageLoading(false);
    }
  };

  const handleUpdateEmployee = async (empCode, data) => {
    try {
      await axios.put(`${API_BASE_URL}/v1/employee/${empCode}`, data);
      await fetchEmployees();
      setEditingEmployee(null);
      setManageError(null);
    } catch (err) {
      setManageError(err.response?.data?.detail || 'Failed to update employee');
    }
  };

  const handleUpdateStore = async (storeId, data) => {
    try {
      await axios.put(`${API_BASE_URL}/v1/stores/${storeId}`, data);
      await fetchStores();
      setEditingStore(null);
      setManageError(null);
    } catch (err) {
      setManageError(err.response?.data?.detail || 'Failed to update store');
    }
  };

  const handleFaceImageSelect = (event) => {
    const files = Array.from(event.target.files);
    setFaceImages(files);
    setFaceRegError(null);
    setFaceRegSuccess(null);
  };

  const startFaceCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' }
      });
      setFaceCameraStream(stream);
      setFaceCameraMode(true);
      setFaceRegError(null);
    } catch (error) {
      setFaceRegError('Failed to access camera: ' + error.message);
      setFaceCameraMode(false);
    }
  };

  const stopFaceCamera = () => {
    if (faceCameraStream) {
      faceCameraStream.getTracks().forEach(track => track.stop());
      if (faceVideoRef.current) {
        faceVideoRef.current.srcObject = null;
      }
      setFaceCameraStream(null);
      setFaceCameraMode(false);
    }
  };

  const captureFacePhoto = () => {
    if (!faceVideoRef.current || !faceCanvasRef.current) return null;

    const video = faceVideoRef.current;
    const canvas = faceCanvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob);
      }, 'image/jpeg', 0.95);
    });
  };

  const captureFaceFromCamera = async () => {
    if (!faceCameraStream) {
      setFaceRegError('Please start camera first');
      return;
    }

    try {
      const photoBlob = await captureFacePhoto();
      if (!photoBlob) {
        setFaceRegError('Failed to capture photo');
        return;
      }

      // Add captured photo to faceImages
      const file = new File([photoBlob], `captured-${Date.now()}.jpg`, { type: 'image/jpeg' });
      setFaceImages(prev => [...prev, file]);
      setFaceRegError(null);
    } catch (error) {
      setFaceRegError('Failed to capture photo: ' + error.message);
    }
  };

  // Effect to handle video stream when both stream and videoRef are ready
  useEffect(() => {
    if (faceCameraStream && faceVideoRef.current) {
      faceVideoRef.current.srcObject = faceCameraStream;
      faceVideoRef.current.onloadedmetadata = () => {
        if (faceVideoRef.current) {
          faceVideoRef.current.play().catch(err => {
            console.error('Error playing video:', err);
          });
        }
      };
    } else if (faceVideoRef.current && !faceCameraStream) {
      faceVideoRef.current.srcObject = null;
    }
  }, [faceCameraStream]);

  // Cleanup camera when component unmounts or editing changes
  useEffect(() => {
    return () => {
      stopFaceCamera();
    };
  }, []);

  useEffect(() => {
    if (!editingFaceEmployee) {
      stopFaceCamera();
    }
  }, [editingFaceEmployee]);

  const handleUpdateFace = async (employeeId) => {
    if (faceImages.length === 0) {
      setFaceRegError('Please select at least one image');
      return;
    }

    setFaceRegLoading(true);
    setFaceRegError(null);
    setFaceRegSuccess(null);

    try {
      const formData = new FormData();
      formData.append('employee_id', employeeId);
      faceImages.forEach((file) => {
        formData.append('images', file);
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

      setFaceRegSuccess(response.data);
      setFaceImages([]);
      setEditingFaceEmployee(null);
      // Refresh employees list
      await fetchEmployees();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to register face';
      setFaceRegError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setFaceRegLoading(false);
    }
  };

  const handleDeleteEmployee = async (employeeId, employeeName) => {
    const confirmMessage = `Are you sure you want to delete employee "${employeeName}" (${employeeId})?\n\nThis will also delete:\n- Face embeddings\n- Schedules\n- Attendance logs\n\nThis action cannot be undone!`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setManageLoading(true);
    setManageError(null);

    try {
      await axios.delete(`${API_BASE_URL}/v1/employee/${employeeId}`);
      // Refresh employees list
      await fetchEmployees();
      setManageError(null);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to delete employee';
      setManageError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setManageLoading(false);
    }
  };

  const fetchSchedulesByStore = async () => {
    setScheduleLoading(true);
    setScheduleError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/v1/schedules/by-store`, {
        params: {
          store_id: scheduleStoreId,
          date: scheduleDate
        }
      });
      setSchedulesByStore(response.data);
    } catch (err) {
      setScheduleError(err.response?.data?.detail || 'Failed to fetch schedules');
    } finally {
      setScheduleLoading(false);
    }
  };

  const handleAddEmployeeToShift = async (shiftNumber) => {
    if (!newEmployeeId.trim()) {
      setScheduleError('Please enter employee ID');
      return;
    }

    setScheduleLoading(true);
    setScheduleError(null);

    try {
      // First, get AI suggestion
      const suggestResponse = await axios.get(`${API_BASE_URL}/v1/schedules/suggest`, {
        params: {
          employee_id: newEmployeeId.trim(),
          store_id: scheduleStoreId,
          date: scheduleDate
        }
      });

      // Create schedule with suggested shift or user-selected shift
      const selectedShift = shiftNumber || suggestResponse.data.suggested_shift;
      
      await axios.post(`${API_BASE_URL}/v1/schedules`, {
        employee_id: newEmployeeId.trim(),
        store_id: scheduleStoreId,
        date: scheduleDate,
        shift_number: selectedShift
      });

      setNewEmployeeId('');
      await fetchSchedulesByStore();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to add employee to schedule';
      setScheduleError(errorMsg);
    } finally {
      setScheduleLoading(false);
    }
  };

  const handleRemoveEmployeeFromShift = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to remove this employee from this shift?')) {
      return;
    }

    setScheduleLoading(true);
    setScheduleError(null);

    try {
      await axios.delete(`${API_BASE_URL}/v1/schedules/${scheduleId}`);
      await fetchSchedulesByStore();
    } catch (err) {
      setScheduleError(err.response?.data?.detail || 'Failed to remove employee from schedule');
    } finally {
      setScheduleLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard' && isAuthenticated) {
      fetchAttendanceData();
    } else if (activeTab === 'history' && isAuthenticated) {
      fetchCheckInHistory();
    } else if (activeTab === 'register') {
      fetchAvailableEmployees();
    } else if (activeTab === 'manage' && isAuthenticated && isManagerOrAdmin) {
      fetchEmployees();
      fetchStores();
    }
  }, [activeTab, isAuthenticated, isManagerOrAdmin]); // Removed attendanceData from dependencies to prevent infinite loop

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
      <div className="dashboard-app">
        <div className="login-prompt">
          <div className="login-prompt-content">
            <h1>🔒 Authentication Required</h1>
            <p>Please check in at the kiosk to access the dashboard.</p>
            <p className="login-instructions">
              Go to the <strong>Check-in Kiosk</strong> and use face recognition to check in.
              After successful check-in, you will be automatically redirected here.
            </p>
            <div className="login-actions">
              <button onClick={() => navigate('/')} className="btn btn-primary">
                Go to Check-in Kiosk
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-app">
      <header className="dashboard-header">
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
            📊 Attendance Reports
          </button>
          <button 
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => setActiveTab('history')}
          >
            📝 Check-in History
          </button>
          <button 
            className={activeTab === 'register' ? 'active' : ''}
            onClick={() => setActiveTab('register')}
          >
            👤 Register Face
          </button>
          {isManagerOrAdmin && (
            <button 
              className={activeTab === 'manage' ? 'active' : ''}
              onClick={() => setActiveTab('manage')}
            >
              ⚙️ Manage
            </button>
          )}
        </nav>
      </header>
      <main className="dashboard-main">
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
        ) : activeTab === 'history' ? (
          <div className="checkin-history">
            <h2>📝 Check-in History</h2>
            {historyLoading && <div className="loading">Loading history...</div>}
            
            {checkInHistory.length === 0 && !historyLoading && (
              <div className="no-data">No check-in records found.</div>
            )}
            
            {checkInHistory.length > 0 && (
              <div className="history-list">
                {checkInHistory.map((record) => (
                  <div key={record.id} className={`history-item ${record.is_on_time === 0 ? 'late-checkin' : ''}`}>
                    <div className="history-header">
                      <div className="history-employee">
                        <strong>{record.employee_name}</strong> ({record.employee_id})
                        {record.employee_role && (
                          <span className="employee-role"> - {record.employee_role}</span>
                        )}
                        {record.is_on_time === 0 && (
                          <span className="late-badge">⚠️ LATE</span>
                        )}
                      </div>
                      <div className="history-time">
                        {new Date(record.timestamp).toLocaleString('vi-VN')}
                      </div>
                    </div>
                    <div className="history-details">
                      <div className="detail-row">
                        <span className="detail-label">Store:</span>
                        <span>{record.store_name || 'N/A'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Camera:</span>
                        <span>{record.camera_name || `Camera ${record.camera_id}`}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Confidence:</span>
                        <span>{(record.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">On Time Status:</span>
                        <span>
                          {record.is_on_time === 0 ? (
                            <span className="status-late">⚠️ Late Check-in</span>
                          ) : record.is_on_time === 1 ? (
                            <span className="status-ontime">✓ On Time</span>
                          ) : (
                            <span className="status-unknown">- Not Checked</span>
                          )}
                        </span>
                      </div>
                      {record.latitude && record.longitude && (
                        <>
                          <div className="detail-row">
                            <span className="detail-label">Location:</span>
                            <span>
                              {record.latitude.toFixed(6)}, {record.longitude.toFixed(6)}
                            </span>
                          </div>
                          {record.distance_from_store !== null && (
                            <div className="detail-row">
                              <span className="detail-label">Distance from Store:</span>
                              <span>
                                {record.distance_from_store.toFixed(2)}m
                                {record.location_validated === 1 && (
                                  <span className="location-valid"> ✓ Valid</span>
                                )}
                                {record.location_validated === 2 && (
                                  <span className="location-invalid"> ✗ Too far</span>
                                )}
                              </span>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : activeTab === 'manage' && isManagerOrAdmin ? (
          <div className="management-section">
            <h2>⚙️ Management</h2>
            {manageError && <div className="error-message">{manageError}</div>}
            
            <div className="manage-tabs">
              <button 
                className={editingEmployee === null && editingStore === null && !schedulesByStore ? 'active' : ''}
                onClick={() => { 
                  setEditingEmployee(null); 
                  setEditingStore(null);
                  setSchedulesByStore(null);
                }}
              >
                Overview
              </button>
              <button 
                className={schedulesByStore ? 'active' : ''}
                onClick={() => {
                  setEditingEmployee(null);
                  setEditingStore(null);
                  fetchSchedulesByStore();
                }}
              >
                📅 Schedules
              </button>
            </div>

            {/* Employees Management */}
            <div className="manage-section">
              <h3>👥 Employees</h3>
              {manageLoading ? (
                <div className="loading">Loading...</div>
              ) : (
                <div className="manage-list">
                  {employees.map((emp) => (
                    <div key={emp.id} className="manage-item">
                      {editingEmployee?.id === emp.id ? (
                        <EmployeeEditForm
                          employee={emp}
                          onSave={(data) => handleUpdateEmployee(emp.emp_code, data)}
                          onCancel={() => setEditingEmployee(null)}
                        />
                      ) : (
                        <>
                          <div className="manage-item-info">
                            <div><strong>ID:</strong> {emp.emp_code}</div>
                            <div><strong>Name:</strong> {emp.name}</div>
                            <div><strong>Role:</strong> {emp.role || 'N/A'}</div>
                          </div>
                          <div className="manage-item-actions">
                            <button 
                              className="btn-edit"
                              onClick={() => setEditingEmployee(emp)}
                            >
                              ✏️ Edit
                            </button>
                            <button 
                              className="btn-edit-face"
                              onClick={() => {
                                setEditingFaceEmployee(emp);
                                setFaceImages([]);
                                setFaceRegError(null);
                                setFaceRegSuccess(null);
                              }}
                            >
                              👤 Edit Face
                            </button>
                            <button 
                              className="btn-delete"
                              onClick={() => handleDeleteEmployee(emp.emp_code, emp.name)}
                              disabled={manageLoading}
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        </>
                      )}
                      {editingFaceEmployee?.id === emp.id && (
                        <div className="face-edit-form">
                          <h4>Update Face for {emp.name}</h4>
                          
                          {/* Camera Mode Toggle */}
                          <div className="camera-mode-toggle">
                            <button
                              type="button"
                              className={faceCameraMode ? 'btn-toggle active' : 'btn-toggle'}
                              onClick={() => {
                                if (faceCameraMode) {
                                  stopFaceCamera();
                                } else {
                                  startFaceCamera();
                                }
                              }}
                              disabled={faceRegLoading}
                            >
                              {faceCameraMode ? '📷 Stop Camera' : '📷 Use Camera'}
                            </button>
                            <span style={{ margin: '0 10px' }}>or</span>
                            <button
                              type="button"
                              className={!faceCameraMode ? 'btn-toggle active' : 'btn-toggle'}
                              onClick={() => {
                                stopFaceCamera();
                              }}
                              disabled={faceRegLoading}
                            >
                              📁 Upload Files
                            </button>
                          </div>

                          {/* Camera Preview */}
                          {faceCameraMode && (
                            <div className="camera-preview-section">
                              <div className="camera-preview">
                                <video 
                                  ref={faceVideoRef} 
                                  autoPlay 
                                  playsInline 
                                  muted 
                                  style={{ 
                                    width: '100%', 
                                    height: '100%', 
                                    objectFit: 'cover',
                                    display: faceCameraStream ? 'block' : 'none'
                                  }}
                                />
                                {!faceCameraStream && (
                                  <div className="camera-placeholder">
                                    Camera not started. Click "Use Camera" to begin.
                                  </div>
                                )}
                                <canvas ref={faceCanvasRef} style={{ display: 'none' }} />
                              </div>
                              <button
                                type="button"
                                className="btn-capture"
                                onClick={captureFaceFromCamera}
                                disabled={!faceCameraStream || faceRegLoading}
                              >
                                📸 Capture Photo
                              </button>
                            </div>
                          )}

                          {/* File Upload */}
                          {!faceCameraMode && (
                            <div className="form-group">
                              <label>Face Images (2-3 images recommended):</label>
                              <input
                                type="file"
                                accept="image/*"
                                multiple
                                onChange={handleFaceImageSelect}
                                disabled={faceRegLoading}
                              />
                            </div>
                          )}

                          {/* Selected Images List */}
                          {faceImages.length > 0 && (
                            <div className="selected-images-list">
                              <p className="info-text">Selected {faceImages.length} image(s):</p>
                              <ul>
                                {faceImages.map((img, idx) => (
                                  <li key={idx}>
                                    {img.name || `Image ${idx + 1}`}
                                    <button
                                      type="button"
                                      className="btn-remove-image"
                                      onClick={() => {
                                        setFaceImages(prev => prev.filter((_, i) => i !== idx));
                                      }}
                                      disabled={faceRegLoading}
                                    >
                                      ×
                                    </button>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {faceRegError && (
                            <div className="error-message">{faceRegError}</div>
                          )}
                          {faceRegSuccess && (
                            <div className="success-message">
                              {faceRegSuccess.message || 'Face updated successfully!'}
                            </div>
                          )}
                          <div className="form-actions">
                            <button
                              className="btn-save"
                              onClick={() => handleUpdateFace(emp.emp_code)}
                              disabled={faceRegLoading || faceImages.length === 0}
                            >
                              {faceRegLoading ? 'Updating...' : '💾 Update Face'}
                            </button>
                            <button
                              className="btn-cancel"
                              onClick={() => {
                                stopFaceCamera();
                                setEditingFaceEmployee(null);
                                setFaceImages([]);
                                setFaceRegError(null);
                                setFaceRegSuccess(null);
                              }}
                              disabled={faceRegLoading}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Stores Management */}
            <div className="manage-section">
              <h3>🏪 Stores</h3>
              {manageLoading ? (
                <div className="loading">Loading...</div>
              ) : (
                <div className="manage-list">
                  {stores.map((store) => (
                    <div key={store.id} className="manage-item">
                      {editingStore?.id === store.id ? (
                        <StoreEditForm
                          store={store}
                          onSave={(data) => handleUpdateStore(store.id, data)}
                          onCancel={() => setEditingStore(null)}
                        />
                      ) : (
                        <>
                          <div className="manage-item-info">
                            <div><strong>ID:</strong> {store.id}</div>
                            <div><strong>Name:</strong> {store.name || 'N/A'}</div>
                            <div><strong>Address:</strong> {store.address || 'N/A'}</div>
                            <div>
                              <strong>Location:</strong> {
                                store.latitude && store.longitude 
                                  ? `${store.latitude.toFixed(6)}, ${store.longitude.toFixed(6)}`
                                  : 'Not set'
                              }
                            </div>
                          </div>
                          <button 
                            className="btn-edit"
                            onClick={() => setEditingStore(store)}
                          >
                            ✏️ Edit
                          </button>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Schedule Management */}
            {schedulesByStore && (
              <div className="manage-section">
                <h3>📅 Schedule Management</h3>
                
                <div className="schedule-filters">
                  <div className="form-group">
                    <label>Store:</label>
                    <select
                      value={scheduleStoreId}
                      onChange={(e) => {
                        setScheduleStoreId(parseInt(e.target.value));
                        setSchedulesByStore(null);
                      }}
                    >
                      {stores.map(store => (
                        <option key={store.id} value={store.id}>
                          {store.name || `Store ${store.id}`}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Date:</label>
                    <input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => {
                        setScheduleDate(e.target.value);
                        setSchedulesByStore(null);
                      }}
                    />
                  </div>
                  <button
                    className="btn-load-schedule"
                    onClick={fetchSchedulesByStore}
                    disabled={scheduleLoading}
                  >
                    {scheduleLoading ? 'Loading...' : '📅 Load Schedule'}
                  </button>
                </div>

                {scheduleError && (
                  <div className="error-message">{scheduleError}</div>
                )}

                {schedulesByStore && (
                  <div className="schedule-table-container">
                    <h4>Schedule for {stores.find(s => s.id === scheduleStoreId)?.name || `Store ${scheduleStoreId}`} - {scheduleDate}</h4>
                    
                    <table className="schedule-table">
                      <thead>
                        <tr>
                          <th>Shift</th>
                          <th>Time</th>
                          <th>Employees</th>
                          <th>Add Employee</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[1, 2, 3, 4].map(shiftNum => {
                          const shiftTimes = {
                            1: '06:00 - 10:00',
                            2: '10:00 - 14:00',
                            3: '14:00 - 18:00',
                            4: '18:00 - 22:00'
                          };
                          const employees = schedulesByStore.shifts[shiftNum] || [];
                          
                          return (
                            <tr key={shiftNum}>
                              <td><strong>Ca {shiftNum}</strong></td>
                              <td>{shiftTimes[shiftNum]}</td>
                              <td>
                                <div className="employee-list">
                                  {employees.length === 0 ? (
                                    <span className="no-employees">No employees assigned</span>
                                  ) : (
                                    employees.map((emp, idx) => (
                                      <span key={idx} className="employee-badge">
                                        {emp.employee_id} ({emp.employee_name})
                                        <button
                                          className="btn-remove-small"
                                          onClick={() => handleRemoveEmployeeFromShift(emp.schedule_id)}
                                          disabled={scheduleLoading}
                                          title="Remove from shift"
                                        >
                                          ×
                                        </button>
                                      </span>
                                    ))
                                  )}
                                </div>
                              </td>
                              <td>
                                <div className="add-employee-cell">
                                  <input
                                    type="text"
                                    placeholder="Employee ID"
                                    value={editingScheduleCell?.shift === shiftNum ? newEmployeeId : ''}
                                    onChange={(e) => {
                                      setNewEmployeeId(e.target.value);
                                      setEditingScheduleCell({ storeId: scheduleStoreId, date: scheduleDate, shift: shiftNum });
                                    }}
                                    onKeyPress={(e) => {
                                      if (e.key === 'Enter') {
                                        handleAddEmployeeToShift(shiftNum);
                                      }
                                    }}
                                    disabled={scheduleLoading}
                                  />
                                  <button
                                    className="btn-add-small"
                                    onClick={() => handleAddEmployeeToShift(shiftNum)}
                                    disabled={scheduleLoading || !newEmployeeId.trim()}
                                  >
                                    ➕ Add
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
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
                  <th>Role</th>
                  <th>Present Days</th>
                  <th>Late Days</th>
                  <th>Total Days</th>
                  <th>Attendance %</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.attendance_summary.map((emp, idx) => (
                  <tr 
                    key={idx}
                    className={emp.late_days > 0 ? 'has-late-checkins' : ''}
                  >
                    <td>{emp.employee_id}</td>
                    <td>{emp.employee_name}</td>
                    <td>{emp.employee_role || 'N/A'}</td>
                    <td>{emp.present_days}</td>
                    <td className={emp.late_days > 0 ? 'late-days' : ''}>
                      {emp.late_days || 0}
                    </td>
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

export default Dashboard;

