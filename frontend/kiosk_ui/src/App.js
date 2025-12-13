import React, { useState, useRef, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import Dashboard from './Dashboard';
import './Dashboard.css';

const API_BASE_URL = '/api';

function CheckIn() {
  const navigate = useNavigate();
  const [cameraId, setCameraId] = useState('1'); // Default camera ID, hidden from UI
  const [stream, setStream] = useState(null);
  const [status, setStatus] = useState({ type: 'info', message: 'Ready to check in' });
  const [checkinResult, setCheckinResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showRegistrationModal, setShowRegistrationModal] = useState(false);
  
  // Registration form state
  const [regEmployeeId, setRegEmployeeId] = useState('');
  const [regName, setRegName] = useState('');
  const [regRole, setRegRole] = useState('');
  const [regImages, setRegImages] = useState([]);
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState(null);
  const [capturedImageForReg, setCapturedImageForReg] = useState(null);
  const [lastImageFile, setLastImageFile] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const regFileInputRef = useRef(null);

  // Fetch available cameras on mount and set default
  const fetchCameras = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/v1/cameras`);
      const camerasList = response.data || [];
      if (camerasList.length > 0) {
        setCameraId(camerasList[0].id.toString());
      }
    } catch (error) {
      console.error('Failed to fetch cameras:', error);
      // Keep default camera ID '1'
    }
  }, []);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  // Effect to handle video stream when both stream and videoRef are ready
  useEffect(() => {
    if (stream && videoRef.current) {
      const video = videoRef.current;
      video.srcObject = stream;
      
      // Ensure video plays when metadata is loaded
      const handleLoadedMetadata = () => {
        video.play().catch(err => {
          console.error('Error playing video:', err);
          setStatus({ type: 'error', message: 'Failed to start video playback' });
        });
      };
      
      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      
      // Cleanup
      return () => {
        video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      };
    }
  }, [stream]);

  const startCamera = async () => {
    try {
      setStatus({ type: 'info', message: 'Requesting camera access...' });
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user', 
          width: { ideal: 1280 }, 
          height: { ideal: 720 } 
        }
      });
      
      setStream(mediaStream);
      setStatus({ type: 'info', message: 'Camera started. Position your face in the frame.' });
    } catch (error) {
      let errorMessage = 'Failed to access camera. ';
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage += 'Please allow camera permissions in your browser settings.';
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage += 'No camera found. Please connect a camera.';
      } else {
        errorMessage += error.message || 'Please check your camera settings.';
      }
      setStatus({ type: 'error', message: errorMessage });
      console.error('Camera error:', error);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      setStream(null);
      setStatus({ type: 'info', message: 'Camera stopped' });
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return null;

    const video = videoRef.current;
    const canvas = canvasRef.current;
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

  const checkInWithCamera = async () => {
    if (!stream) {
      setStatus({ type: 'error', message: 'Please start camera first' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'loading', message: 'Capturing photo and checking in...' });
    setCheckinResult(null);

    try {
      const photoBlob = await capturePhoto();
      if (!photoBlob) {
        throw new Error('Failed to capture photo');
      }

      await performCheckIn(photoBlob);
    } catch (error) {
      // Error handling is done in performCheckIn
      // This catch is just for photo capture errors
      if (error.message && !error.message.includes('Check-in failed')) {
        const errorMsg = typeof error.message === 'string' ? error.message : String(error.message || 'Failed to capture photo');
        setStatus({ type: 'error', message: errorMsg });
        setLoading(false);
      }
    }
  };


  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser'));
        return;
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => {
          console.warn('Failed to get location:', error);
          resolve(null); // Don't fail check-in if location fails
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      );
    });
  };

  const performCheckIn = async (imageFile) => {
    // Save image file for potential registration
    setLastImageFile(imageFile);
    
    try {
      // Get GPS location
      let location = null;
      try {
        location = await getCurrentLocation();
      } catch (error) {
        console.warn('Location not available:', error);
      }

      const formData = new FormData();
      formData.append('camera_id', cameraId);
      formData.append('image', imageFile);
      
      if (location) {
        formData.append('latitude', location.latitude.toString());
        formData.append('longitude', location.longitude.toString());
      }

      const response = await axios.post(
        `${API_BASE_URL}/v1/attendance/check-in`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      const result = response.data;
      setCheckinResult({
        employeeId: result.employee_id,
        employeeName: result.employee_name,
        timestamp: result.timestamp,
        confidence: result.confidence,
        cameraId: result.camera_id,
        latitude: result.latitude,
        longitude: result.longitude,
        locationValidated: result.location_validated,
        distanceFromStore: result.distance_from_store,
      });

      setStatus({
        type: 'success',
        message: `Check-in successful! Welcome ${result.employee_name}. Redirecting to dashboard...`,
      });

      // Store session
      try {
        localStorage.setItem('auth_employee_id', result.employee_id);
        localStorage.setItem('auth_employee_name', result.employee_name);
        localStorage.setItem('auth_timestamp', new Date().toISOString());
        
        // Fetch and store employee role
        try {
          const empResponse = await axios.get(`${API_BASE_URL}/v1/employee/${result.employee_id}`);
          if (empResponse.data && empResponse.data.role) {
            localStorage.setItem('auth_employee_role', empResponse.data.role);
          }
        } catch (err) {
          console.warn('Failed to fetch employee role:', err);
        }
        
        // Verify localStorage was set
        const storedId = localStorage.getItem('auth_employee_id');
        const storedName = localStorage.getItem('auth_employee_name');
        const storedTimestamp = localStorage.getItem('auth_timestamp');
        
        console.log('Session stored:', {
          employee_id: storedId,
          employee_name: storedName,
          timestamp: storedTimestamp
        });
        
        if (!storedId || !storedName || !storedTimestamp) {
          console.error('Failed to store session in localStorage!');
        }
      } catch (storageError) {
        console.error('Error storing session:', storageError);
      }
      
      // Redirect to dashboard after 1 second using React Router
      console.log('Will redirect to dashboard in 1 second');
      
      setTimeout(() => {
        try {
          console.log('Executing redirect to /dashboard');
          navigate('/dashboard', { replace: true });
        } catch (error) {
          console.error('Redirect failed:', error);
          alert('Check-in successful! Please navigate to /dashboard');
        }
      }, 1000);
    } catch (error) {
      let errorMsg = 'Check-in failed';
      let shouldShowRegistration = false;
      let isSpoofingDetected = false;
      
      if (error.response) {
        // Handle different error response formats
        const responseData = error.response.data;
        const statusCode = error.response.status;
        
        if (typeof responseData === 'string') {
          errorMsg = responseData;
        } else if (responseData?.detail) {
          // Handle detail field - could be string or array
          if (typeof responseData.detail === 'string') {
            errorMsg = responseData.detail;
          } else if (Array.isArray(responseData.detail)) {
            // FastAPI validation errors array
            errorMsg = responseData.detail
              .map(err => {
                if (typeof err === 'string') return err;
                if (typeof err === 'object' && err !== null) {
                  const msg = err.msg || err.message || 'Invalid value';
                  const loc = Array.isArray(err.loc) ? err.loc.join('.') : '';
                  const result = loc ? `${loc}: ${msg}` : String(msg);
                  return typeof result === 'string' ? result : String(result);
                }
                return String(err);
              })
              .filter(msg => msg && typeof msg === 'string' && msg.trim())
              .join(', ') || 'Validation error';
          } else if (typeof responseData.detail === 'object') {
            errorMsg = JSON.stringify(responseData.detail);
          }
        } else if (responseData?.message) {
          errorMsg = typeof responseData.message === 'string'
            ? responseData.message
            : JSON.stringify(responseData.message);
        } else if (Array.isArray(responseData)) {
          errorMsg = responseData
            .map(err => {
              if (typeof err === 'string') return err;
              if (typeof err === 'object' && err !== null) {
                const msg = err.msg || err.message || 'Invalid value';
                const loc = Array.isArray(err.loc) ? err.loc.join('.') : '';
                const result = loc ? `${loc}: ${msg}` : String(msg);
                return typeof result === 'string' ? result : String(result);
              }
              return String(err);
            })
            .filter(msg => msg && typeof msg === 'string' && msg.trim())
            .join(', ') || 'Validation error';
        } else if (typeof responseData === 'object') {
          errorMsg = JSON.stringify(responseData);
        }
        
        const errorMsgLower = errorMsg.toLowerCase();
        
        // Check for spoofing detection (403 Forbidden)
        if (statusCode === 403) {
          const spoofingKeywords = ['spoofing', 'spoof', 'photo', 'picture', 'live face', 'liveness'];
          isSpoofingDetected = spoofingKeywords.some(keyword => errorMsgLower.includes(keyword));
          
          if (isSpoofingDetected) {
            errorMsg = '⚠️ Detected use of photo instead of live face. Please use camera to scan your face directly.';
            setStatus({ type: 'error', message: errorMsg });
            setLoading(false);
            return;
          }
        }
        
        // Check if this is a face recognition error (not spoofing)
        const faceErrorKeywords = [
          'not recognized',
          'no face detected',
          'invalid face embedding',
          'face not found',
          'employee not found',
          'no face',
          'not found',
          'unrecognized',
          'best match confidence',
          'threshold',
          'no faces detected',
          'face detection failed'
        ];
        
        // For 404, 400, or 500 errors, check if it's face-related
        if (statusCode === 404 || statusCode === 400 || statusCode === 500) {
          if (errorMsgLower.includes('camera not found')) {
            shouldShowRegistration = false;
            errorMsg = 'Camera not found. Please contact administrator.';
          } else {
            // Check if any face-related keyword matches
            shouldShowRegistration = faceErrorKeywords.some(keyword => errorMsgLower.includes(keyword));
            
            if (shouldShowRegistration) {
              errorMsg = '❌ Face not recognized. Please register your account.';
            }
          }
        }
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      // If face recognition error (not spoofing), show registration modal
      if (shouldShowRegistration && !isSpoofingDetected) {
        // Save the captured image for registration
        if (imageFile instanceof Blob) {
          setCapturedImageForReg(imageFile);
        }
        setShowRegistrationModal(true);
        setStatus({ type: 'error', message: errorMsg });
        setLoading(false);
        return;
      }
      
      // For other errors, show error message
      setStatus({ type: 'error', message: errorMsg });
      setLoading(false);
    }
  };

  const handleRegistration = async () => {
    if (!regEmployeeId.trim() || !regName.trim() || !regRole.trim()) {
      setRegError('Please fill in all fields');
      return;
    }

    if (regImages.length < 2 && !capturedImageForReg) {
      setRegError('Please select at least 2-3 images or use the captured photo');
      return;
    }

    setRegLoading(true);
    setRegError(null);

    try {
      // Step 1: Create employee account
      const employeeData = {
        emp_code: regEmployeeId.trim(),
        name: regName.trim(),
        role: regRole.trim()
      };

      try {
        await axios.post(`${API_BASE_URL}/v1/employee`, employeeData);
      } catch (err) {
        if (err.response?.status === 400 && err.response?.data?.detail?.includes('already exists')) {
          // Employee exists, that's okay - just register face
        } else {
          throw err;
        }
      }

      // Step 2: Register face with images
      const formData = new FormData();
      formData.append('employee_id', regEmployeeId.trim());
      
      // Add captured image if available
      if (capturedImageForReg) {
        formData.append('images', capturedImageForReg);
      }
      
      // Add selected images
      regImages.forEach((img) => {
        formData.append('images', img);
      });

      await axios.post(
        `${API_BASE_URL}/v1/employee/register-face`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Success! Save captured image for auto check-in
      const imageToCheckIn = capturedImageForReg;
      
      // Close modal and clear form
      setShowRegistrationModal(false);
      setRegEmployeeId('');
      setRegName('');
      setRegRole('');
      setRegImages([]);
      setCapturedImageForReg(null);
      setStatus({ type: 'success', message: 'Registration successful! Checking in...' });
      
      // Auto check-in after registration
      if (imageToCheckIn) {
        setTimeout(async () => {
          try {
            setLoading(true);
            await performCheckIn(imageToCheckIn);
            // performCheckIn will handle redirect on success
          } catch (error) {
            // Error already handled in performCheckIn
            console.error('Auto check-in after registration failed:', error);
            setLoading(false);
            // Show message to user
            setStatus({ 
              type: 'error', 
              message: 'Registration successful, but auto check-in failed. Please try checking in manually.' 
            });
          }
        }, 1000);
      } else {
        setStatus({ type: 'info', message: 'Registration successful! Please check in with camera.' });
      }
    } catch (error) {
      let errorMsg = 'Registration failed. Please try again.';
      
      if (error.response) {
        const responseData = error.response.data;
        
        if (typeof responseData === 'string') {
          errorMsg = responseData;
        } else if (responseData?.detail) {
          if (typeof responseData.detail === 'string') {
            errorMsg = responseData.detail;
          } else if (Array.isArray(responseData.detail)) {
            // FastAPI validation errors array
            errorMsg = responseData.detail
              .map(err => {
                if (typeof err === 'string') return err;
                if (typeof err === 'object' && err !== null) {
                  const msg = err.msg || err.message || 'Invalid value';
                  const loc = Array.isArray(err.loc) ? err.loc.join('.') : '';
                  const result = loc ? `${loc}: ${msg}` : String(msg);
                  return typeof result === 'string' ? result : String(result);
                }
                return String(err);
              })
              .filter(msg => msg && typeof msg === 'string' && msg.trim())
              .join(', ') || 'Validation error';
          } else if (typeof responseData.detail === 'object') {
            errorMsg = JSON.stringify(responseData.detail);
          }
        } else if (responseData?.message) {
          errorMsg = typeof responseData.message === 'string'
            ? responseData.message
            : String(responseData.message);
        } else if (Array.isArray(responseData)) {
          errorMsg = responseData
            .map(err => {
              if (typeof err === 'string') return err;
              if (typeof err === 'object' && err !== null) {
                const msg = err.msg || err.message || 'Invalid value';
                const loc = Array.isArray(err.loc) ? err.loc.join('.') : '';
                const result = loc ? `${loc}: ${msg}` : String(msg);
                return typeof result === 'string' ? result : String(result);
              }
              return String(err);
            })
            .filter(msg => msg && typeof msg === 'string' && msg.trim())
            .join(', ') || 'Validation error';
        } else if (typeof responseData === 'object') {
          errorMsg = JSON.stringify(responseData);
        }
      } else if (error.message) {
        errorMsg = typeof error.message === 'string' ? error.message : String(error.message);
      }
      
      setRegError(errorMsg);
    } finally {
      setRegLoading(false);
    }
  };

  const handleRegImageSelect = (event) => {
    const files = Array.from(event.target.files);
    setRegImages(files);
    setRegError(null);
  };

  return (
    <div className="App">
      <div className="kiosk-container">
        <h1 className="kiosk-title">AI Attendance System</h1>
        <p className="kiosk-subtitle">Face Recognition Check-in</p>

        <div className="camera-section">
          <div className="camera-preview">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'cover',
                display: stream ? 'block' : 'none'
              }}
            />
            {!stream && (
              <div className="camera-placeholder">
                Camera not started. Click "Start Camera" to begin.
              </div>
            )}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </div>

          <div className="controls">
            {!stream ? (
              <button className="btn btn-primary" onClick={startCamera}>
                Start Camera
              </button>
            ) : (
              <>
                <button
                  className="btn btn-primary"
                  onClick={checkInWithCamera}
                  disabled={loading}
                >
                  {loading ? 'Checking In...' : 'Check In with Camera'}
                </button>
                <button className="btn btn-secondary" onClick={stopCamera}>
                  Stop Camera
                </button>
              </>
            )}
          </div>
        </div>

        {status.message && (
          <div className={`status-message status-${status.type}`}>
            {typeof status.message === 'string' ? status.message : String(status.message || '')}
            {status.showRegisterButton && (
              <div style={{ marginTop: '15px' }}>
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    // Save the captured image for registration if available
                    if (lastImageFile instanceof Blob) {
                      setCapturedImageForReg(lastImageFile);
                    }
                    setShowRegistrationModal(true);
                  }}
                >
                  Register Your Account
                </button>
              </div>
            )}
          </div>
        )}

        {checkinResult && (
          <div className="checkin-result">
            <h3>✓ Check-in Successful</h3>
            <div className="checkin-details">
              <p><strong>Employee ID:</strong> {checkinResult.employeeId}</p>
              <p><strong>Name:</strong> {checkinResult.employeeName}</p>
              <p><strong>Time:</strong> {new Date(checkinResult.timestamp).toLocaleString('en-US')}</p>
              <p><strong>Confidence:</strong> {(checkinResult.confidence * 100).toFixed(1)}%</p>
              {checkinResult.latitude && checkinResult.longitude && (
                <>
                  <p><strong>Location:</strong> {checkinResult.latitude.toFixed(6)}, {checkinResult.longitude.toFixed(6)}</p>
                  {checkinResult.distanceFromStore !== null && checkinResult.distanceFromStore !== undefined && (
                    <p>
                      <strong>Distance from Store:</strong> {checkinResult.distanceFromStore.toFixed(2)}m
                      {checkinResult.locationValidated ? (
                        <span style={{ color: '#28a745', marginLeft: '10px', fontWeight: '600' }}>✓ Valid Location</span>
                      ) : checkinResult.distanceFromStore > 10 ? (
                        <span style={{ color: '#dc3545', marginLeft: '10px', fontWeight: '600' }}>✗ Too far from store</span>
                      ) : null}
                    </p>
                  )}
                </>
              )}
            </div>
            <p style={{ marginTop: '15px', color: '#667eea', fontWeight: '600' }}>
              Redirecting to dashboard...
            </p>
            <div style={{ marginTop: '20px' }}>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  console.log('Manual redirect to dashboard');
                  navigate('/dashboard', { replace: true });
                }}
                style={{ marginRight: '10px' }}
              >
                Go to Dashboard Now
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setCheckinResult(null);
                  setStatus({ type: 'info', message: 'Ready to check in' });
                }}
              >
                Check In Again
              </button>
            </div>
          </div>
        )}

        {/* Registration Modal */}
        {showRegistrationModal && (
          <div className="modal-overlay" onClick={() => !regLoading && setShowRegistrationModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Register Your Account</h2>
                <button 
                  className="modal-close" 
                  onClick={() => setShowRegistrationModal(false)}
                  disabled={regLoading}
                >
                  ×
                </button>
              </div>
              
              <div className="modal-body">
                <p className="modal-description">
                  Your face was not recognized. Please register your account to continue.
                </p>

                <div className="form-group">
                  <label htmlFor="reg-employee-id">Employee ID:</label>
                  <input
                    id="reg-employee-id"
                    type="text"
                    value={regEmployeeId}
                    onChange={(e) => setRegEmployeeId(e.target.value)}
                    placeholder="e.g., E003"
                    disabled={regLoading}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="reg-name">Full Name:</label>
                  <input
                    id="reg-name"
                    type="text"
                    value={regName}
                    onChange={(e) => setRegName(e.target.value)}
                    placeholder="Your full name"
                    disabled={regLoading}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="reg-role">Role:</label>
                  <input
                    id="reg-role"
                    type="text"
                    value={regRole}
                    onChange={(e) => setRegRole(e.target.value)}
                    placeholder="e.g., Barista, Manager"
                    disabled={regLoading}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="reg-images">Face Images (2-3 images recommended):</label>
                  {capturedImageForReg && (
                    <p className="info-text">✓ Using captured photo from check-in</p>
                  )}
                  <input
                    ref={regFileInputRef}
                    id="reg-images"
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleRegImageSelect}
                    disabled={regLoading}
                  />
                  {regImages.length > 0 && (
                    <p className="info-text">Selected {regImages.length} additional image(s)</p>
                  )}
                </div>

                {regError && (
                  <div className="error-message">{typeof regError === 'string' ? regError : String(regError)}</div>
                )}

                <div className="modal-actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleRegistration}
                    disabled={regLoading}
                  >
                    {regLoading ? 'Registering...' : 'Register & Check In'}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowRegistrationModal(false)}
                    disabled={regLoading}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CheckIn />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


