import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ParticipantForm from './components/ParticipantForm';
import ParticipantList from './components/ParticipantList';
import CertificatePreview from './components/CertificatePreview';
import BulkUpload from './components/BulkUpload';
import ConferenceRegistration from './components/ConferenceRegistration';
import ProgramSchedule from './components/ProgramSchedule';
import ParticipantDashboard from './components/ParticipantDashboard';
import AdminDashboard from './components/AdminDashboard';
import NotificationCenter from './components/NotificationCenter';
import AttendanceManagement from './components/AttendanceManagement';
import MaterialsUpload from './components/MaterialsUpload';
import AnnouncementManagement from './components/AnnouncementManagement';
import CheckInSystem from './components/CheckInSystem';

// Import styles
import './slideshow.css';
import './conference-info.css';

// Import flier images for slideshow
import flier1 from './flier1.png';
import flier2 from './flier2.png';
import flier3 from './flier3.png';
import mdcanLogo from './logo-mdcan.jpeg';

// Import configuration
import config from './config';

// Set up axios defaults
axios.defaults.baseURL = process.env.REACT_APP_API_URL || config.API_URL;

function App() {
  const [activeTab, setActiveTab] = useState('registration');
  const [participants, setParticipants] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [userType, setUserType] = useState('participant'); // participant, admin
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [message, setMessage] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  // Countdown timer state
  const [timeRemaining, setTimeRemaining] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });
  // Slideshow state
  const flierImages = [
    flier1,
    flier2,
    flier3
  ];
  const [currentSlide, setCurrentSlide] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [deviceType, setDeviceType] = useState('desktop'); // desktop, tablet, mobile
  
  // Detect device type on load
  useEffect(() => {
    const checkDeviceType = async () => {
      try {
        const response = await axios.get('/api/health');
        if (response.data.client && response.data.client.device_type) {
          setDeviceType(response.data.client.device_type);
          // Auto-adjust UI based on device type
          if (response.data.client.device_type === 'mobile') {
            document.body.classList.add('mobile-device');
          } else if (response.data.client.device_type === 'tablet') {
            document.body.classList.add('tablet-device');
          }
        }
      } catch (error) {
        console.error('Error detecting device type:', error);
      }
    };
    
    checkDeviceType();
  }, []);
  
  // Slideshow timer
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % flierImages.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [flierImages.length]);
  
  // Monitor window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
      if (window.innerWidth > 768) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Countdown timer calculation
  useEffect(() => {
    const targetDate = new Date('September 1, 2025 00:00:00').getTime();
    
    const updateCountdown = () => {
      const now = new Date().getTime();
      const difference = targetDate - now;
      
      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        setTimeRemaining({ days, hours, minutes, seconds });
      }
    };
    
    // Initial update
    updateCountdown();
    
    // Update every second
    const interval = setInterval(updateCountdown, 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Load initial data
  useEffect(() => {
    if (userType === 'admin') {
      loadParticipants();
      loadPrograms();
      loadNotifications();
      loadStats();
    }
  }, [userType]);

  // Auto-refresh data every 30 seconds for admin
  useEffect(() => {
    if (userType === 'admin') {
      const interval = setInterval(() => {
        loadStats();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [userType]);

  // Reload participants when switching to participants tab
  useEffect(() => {
    if (userType === 'admin' && activeTab === 'participants') {
      loadParticipants();
    }
  }, [activeTab, userType]);

  const loadParticipants = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/participants');
      // Handle the API response structure: { count: number, participants: array }
      const participantsData = Array.isArray(response.data.participants) ? response.data.participants : 
                              Array.isArray(response.data) ? response.data : [];
      setParticipants(participantsData);
    } catch (error) {
      console.error('Error loading participants:', error);
      setMessage('Failed to load participants');
    } finally {
      setLoading(false);
    }
  };

  const loadPrograms = async () => {
    try {
      const response = await axios.get('/api/programs');
      setPrograms(response.data);
    } catch (error) {
      console.error('Error loading programs:', error);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await axios.get('/api/notifications');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleParticipantAdded = (newParticipant) => {
    setParticipants([newParticipant, ...participants]);
    loadStats();
  };

  const handleBulkUpload = () => {
    loadParticipants();
    loadStats();
  };

  const handleProgramAdded = (newProgram) => {
    setPrograms([newProgram, ...programs]);
  };

  const handleNotificationSent = () => {
    loadNotifications();
  };

  const loginAsParticipant = async (email) => {
    try {
      const response = await axios.get(`/api/participants/${email}/dashboard`);
      // Extract participant data from the dashboard response
      const participantData = response.data.dashboard?.participant || response.data.participant;
      if (participantData) {
        setCurrentUser(participantData);
        setUserType('participant');
        setActiveTab('dashboard');
        setMessage(`Welcome back, ${participantData.name}! Dashboard loaded successfully.`);
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Unable to load participant data. Please try again.');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.response?.status === 404) {
        setMessage('Participant not found. Please check your email or register first.');
      } else {
        setMessage('Error accessing dashboard. Please try again later.');
      }
    }
  };

  const switchToAdmin = () => {
    if (isAdminAuthenticated) {
      setUserType('admin');
      setCurrentUser(null);
      setActiveTab('admin-dashboard');
    } else {
      setShowAdminLogin(true);
    }
  };

  const handleAdminLogin = () => {
    if (adminPassword === 'redvelvet') {
      setIsAdminAuthenticated(true);
      setUserType('admin');
      setCurrentUser(null);
      setActiveTab('admin-dashboard');
      setShowAdminLogin(false);
      setAdminPassword('');
      setMessage('Admin authentication successful!');
      setTimeout(() => setMessage(''), 3000);
    } else {
      setMessage('Invalid admin password. Please try again.');
      setTimeout(() => setMessage(''), 3000);
      setAdminPassword('');
    }
  };

  const handleAdminLogout = () => {
    setIsAdminAuthenticated(false);
    setUserType('participant');
    setCurrentUser(null);
    setActiveTab('registration');
    setMessage('Admin logged out successfully.');
    setTimeout(() => setMessage(''), 3000);
  };

  const switchToParticipant = () => {
    setUserType('participant');
    setCurrentUser(null);
    setActiveTab('registration');
  };

  // Legacy functions for backward compatibility
  const addParticipant = async (participantData) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/participants', participantData);
      setParticipants([...participants, response.data]);
      setMessage('Participant added successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error adding participant:', error);
      setMessage('Error adding participant. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendCertificate = async (participantId) => {
    try {
      setLoading(true);
      await axios.post(`/api/send-certificate/${participantId}`);
      setMessage('Certificate sent successfully!');
      loadParticipants(); // Refresh list to update status
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error sending certificate:', error);
      setMessage('Error sending certificate. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendAllCertificates = async () => {
    try {
      setLoading(true);
      await axios.post('/api/send-all-certificates');
      setMessage('All certificates sent successfully!');
      loadParticipants(); // Refresh list to update statuses
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error sending certificates:', error);
      setMessage('Error sending certificates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <img src={mdcanLogo} alt="MDCAN Logo" className="logo" />
            <div className="event-info">
              <h1>BDM 14th - 2025</h1>
              <p>Conference Registration & Certificate Platform</p>
              <span className="event-details">Enugu • September 1-6, 2025</span>
            </div>
          </div>
          
          {windowWidth <= 768 && (
            <button 
              className="mobile-menu-toggle" 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? '✕' : '☰'}
            </button>
          )}
          
          <div className={`user-controls ${mobileMenuOpen ? 'mobile-open' : ''}`}>
            <div className="user-type-selector">
              <button 
                className={userType === 'participant' ? 'active' : ''}
                onClick={switchToParticipant}
              >
                👤 Participant Portal
              </button>
              <button 
                className={userType === 'admin' ? 'active' : ''}
                onClick={switchToAdmin}
              >
                🛠️ Admin Portal {isAdminAuthenticated ? '(Authenticated)' : '(Login Required)'}
              </button>
              {userType === 'admin' && isAdminAuthenticated && (
                <button 
                  onClick={handleAdminLogout}
                  className="logout-btn"
                  style={{marginLeft: '10px', backgroundColor: '#dc3545', color: 'white'}}
                >
                  🚪 Logout
                </button>
              )}
            </div>
            
            {userType === 'participant' && !currentUser && (
              <div className="login-section">
                <button 
                  onClick={() => {
                    const email = prompt('Enter your email to access your dashboard:');
                    if (email) loginAsParticipant(email);
                  }}
                  className="login-btn"
                >
                  📋 Access My Dashboard
                </button>
              </div>
            )}
            
            {currentUser && (
              <div className="user-info">
                <span>Welcome, {currentUser.name}</span>
                <button onClick={switchToParticipant} className="logout-btn">Logout</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Countdown Banner */}
      <div className="countdown-banner">
        <div className="organization-name">MEDICAL AND DENTAL CONSULTANTS' ASSOCIATION OF NIGERIA</div>
        <div className="countdown-timer">
          <div className="countdown-container">
            <div className="countdown-item">
              <div className="countdown-value">{timeRemaining.days}</div>
              <div className="countdown-label">DAYS</div>
            </div>
            <div className="countdown-separator">:</div>
            <div className="countdown-item">
              <div className="countdown-value">{timeRemaining.hours}</div>
              <div className="countdown-label">HOURS</div>
            </div>
            <div className="countdown-separator">:</div>
            <div className="countdown-item">
              <div className="countdown-value">{timeRemaining.minutes}</div>
              <div className="countdown-label">MINS</div>
            </div>
            <div className="countdown-separator">:</div>
            <div className="countdown-item">
              <div className="countdown-value">{timeRemaining.seconds}</div>
              <div className="countdown-label">SECS</div>
            </div>
          </div>
          <div className="countdown-text">UNTIL THE CONFERENCE</div>
        </div>
      </div>

      {/* Flier Slideshow */}
      <div className="flier-slideshow">
        {flierImages.map((image, index) => (
          <div 
            key={index} 
            className={index === currentSlide ? "slideshow-slide active" : "slideshow-slide"}
          >
            <img src={image} alt={`Conference Flier ${index + 1}`} className="slideshow-image" />
          </div>
        ))}
      </div>

      {/* Navigation */}
      <nav className="app-nav">
        {userType === 'participant' ? (
          // Participant Navigation
          <div className="nav-tabs">
            <button 
              className={activeTab === 'registration' ? 'active' : ''}
              onClick={() => setActiveTab('registration')}
            >
              📝 Conference Registration
            </button>
            <button 
              className={activeTab === 'schedule' ? 'active' : ''}
              onClick={() => setActiveTab('schedule')}
            >
              📅 Program Schedule
            </button>
            {currentUser && (
              <button 
                className={activeTab === 'dashboard' ? 'active' : ''}
                onClick={() => setActiveTab('dashboard')}
              >
                📊 My Dashboard
              </button>
            )}
            <button 
              className={activeTab === 'certificate-preview' ? 'active' : ''}
              onClick={() => setActiveTab('certificate-preview')}
            >
              🏆 Certificate Preview
            </button>
          </div>
        ) : userType === 'admin' && isAdminAuthenticated ? (
          // Admin Navigation (Authenticated)
          <div className="nav-tabs">
            <button 
              className={activeTab === 'admin-dashboard' ? 'active' : ''}
              onClick={() => setActiveTab('admin-dashboard')}
            >
              📊 Admin Dashboard
            </button>
            <button 
              className={activeTab === 'participants' ? 'active' : ''}
              onClick={() => setActiveTab('participants')}
            >
              👥 Participants ({participants.length})
            </button>
            <button 
              className={activeTab === 'add-participant' ? 'active' : ''}
              onClick={() => setActiveTab('add-participant')}
            >
              ➕ Add Participant
            </button>
            <button 
              className={activeTab === 'bulk-upload' ? 'active' : ''}
              onClick={() => setActiveTab('bulk-upload')}
            >
              📤 Bulk Upload
            </button>
            <button 
              className={activeTab === 'programs' ? 'active' : ''}
              onClick={() => setActiveTab('programs')}
            >
              🎯 Program Management
            </button>
            <button 
              className={activeTab === 'notifications' ? 'active' : ''}
              onClick={() => setActiveTab('notifications')}
            >
              🔔 Notifications
            </button>
            <button 
              className={activeTab === 'attendance' ? 'active' : ''}
              onClick={() => setActiveTab('attendance')}
            >
              ✅ Attendance
            </button>
            <button 
              className={activeTab === 'materials' ? 'active' : ''}
              onClick={() => setActiveTab('materials')}
            >
              📚 Materials Upload
            </button>
            <button 
              className={activeTab === 'announcements' ? 'active' : ''}
              onClick={() => setActiveTab('announcements')}
            >
              📢 Announcements
            </button>
            <button 
              className={activeTab === 'check-in' ? 'active' : ''}
              onClick={() => setActiveTab('check-in')}
            >
              🔖 Check-In System
            </button>
            <button 
              className={activeTab === 'certificate-preview' ? 'active' : ''}
              onClick={() => setActiveTab('certificate-preview')}
            >
              🏆 Certificate Preview
            </button>
          </div>
        ) : (
          // Admin not authenticated - show message
          <div className="nav-tabs">
            <div className="admin-auth-message">
              <p>🔐 Please authenticate to access admin features</p>
            </div>
          </div>
        )}
      </nav>

      {/* Message Display */}
      {message && (
        <div className={`message ${message.includes('Error') || message.includes('Failed') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {/* Statistics Bar (Admin only) */}
      {userType === 'admin' && isAdminAuthenticated && stats.participants && (
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-number">{stats.participants.total}</span>
            <span className="stat-label">Total Registered</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.participants.certificates_sent}</span>
            <span className="stat-label">Certificates Sent</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.participants.certificates_pending}</span>
            <span className="stat-label">Certificates Pending</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.recent_activity?.registrations_today || 0}</span>
            <span className="stat-label">Registered Today</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="app-main">
        {loading && <div className="loading-spinner">Loading...</div>}
        
        {/* Participant Portal */}
        {userType === 'participant' && (
          <>
            {activeTab === 'registration' && (
              <ConferenceRegistration 
                onRegistrationSuccess={(participant) => {
                  setCurrentUser(participant);
                  setActiveTab('dashboard');
                  setMessage('Registration successful! Welcome to MDCAN BDM 2025.');
                }}
              />
            )}
            
            {activeTab === 'schedule' && (
              <ProgramSchedule 
                currentUser={currentUser}
                onSessionRegister={() => {
                  if (currentUser) loginAsParticipant(currentUser.email);
                }}
              />
            )}
            
            {activeTab === 'dashboard' && currentUser && (
              <ParticipantDashboard 
                participantEmail={currentUser.email}
                onDataUpdate={() => loginAsParticipant(currentUser.email)}
              />
            )}
            
            {activeTab === 'certificate-preview' && (
              <CertificatePreview participantName="[Participant's Name]" />
            )}
          </>
        )}

        {/* Admin Portal */}
        {userType === 'admin' && isAdminAuthenticated && (
          <>
            {activeTab === 'admin-dashboard' && (
              <AdminDashboard 
                stats={stats}
                onRefresh={loadStats}
              />
            )}
            
            {activeTab === 'participants' && (
              <ParticipantList 
                participants={participants}
                onSendCertificate={sendCertificate}
                onSendAllCertificates={sendAllCertificates}
                loading={loading}
                onRefresh={loadParticipants}
              />
            )}
            
            {activeTab === 'add-participant' && (
              <ParticipantForm 
                onSubmit={addParticipant}
                onParticipantAdded={handleParticipantAdded} 
                loading={loading} 
              />
            )}
            
            {activeTab === 'bulk-upload' && (
              <BulkUpload 
                onParticipantsUpdated={handleBulkUpload}
                onUploadComplete={handleBulkUpload} 
              />
            )}
            
            {activeTab === 'programs' && (
              <ProgramSchedule 
                isAdmin={true}
                programs={programs}
                onProgramAdded={handleProgramAdded}
                onRefresh={loadPrograms}
              />
            )}
            
            {activeTab === 'notifications' && (
              <NotificationCenter 
                notifications={notifications}
                programs={programs}
                onNotificationSent={handleNotificationSent}
              />
            )}
            
            {activeTab === 'attendance' && (
              <AttendanceManagement 
                programs={programs}
                participants={participants}
                onAttendanceUpdate={loadParticipants}
              />
            )}
            
            {activeTab === 'certificate-preview' && (
              <CertificatePreview participantName="[Participant's Name]" />
            )}
            
            {activeTab === 'materials' && (
              <MaterialsUpload />
            )}
            
            {activeTab === 'announcements' && (
              <AnnouncementManagement />
            )}
            
            {activeTab === 'check-in' && (
              <CheckInSystem />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>MDCAN BDM 14th - 2025</h4>
            <p>Medical and Dental Consultants Association of Nigeria</p>
            <p>Branch Delegates Meeting</p>
          </div>
          
          <div className="footer-section">
            <h4>Conference Details</h4>
            <p>📅 September 1-6, 2025</p>
            <p>📍 Enugu, Nigeria</p>
            <p>🎯 Professional Development & Networking</p>
          </div>
          
          <div className="footer-section">
            <h4>Leadership</h4>
            <p><strong>Prof. Aminu Mohammed</strong><br />MDCAN President</p>
            <p><strong>Prof. Appolos Ndukuba</strong><br />LOC Chairman</p>
          </div>
          
          <div className="footer-section">
            <h4>Platform Status</h4>
            <p>🟢 Online & Operational</p>
            <p>🔒 Secure Registration</p>
            <p>📧 Email Notifications Active</p>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 MDCAN BDM. All rights reserved. | Certificate Generation Platform v2.0</p>
        </div>
      </footer>

      {/* Admin Login Modal */}
      {showAdminLogin && (
        <div className="modal-overlay" onClick={() => setShowAdminLogin(false)}>
          <div className="modal-content admin-login-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🔐 Admin Authentication Required</h3>
              <button 
                className="modal-close" 
                onClick={() => setShowAdminLogin(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Please enter the admin password to access the admin portal:</p>
              <div className="form-group">
                <label>Admin Password:</label>
                <input
                  type="password"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAdminLogin()}
                  placeholder="Enter admin password"
                  autoFocus
                />
              </div>
              <div className="modal-actions">
                <button 
                  onClick={handleAdminLogin}
                  className="btn-primary"
                  disabled={!adminPassword.trim()}
                >
                  🔓 Login
                </button>
                <button 
                  onClick={() => setShowAdminLogin(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
