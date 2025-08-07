import React, { useState, useEffect, useCallback } from 'react';
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
import apiService from './services/apiService'; // Import optimized API service

// Import flier images for slideshow
import flier1 from './flier1.png';
import flier2 from './flier2.png';
import flier3 from './flier3.png';
import mdcanLogo from './logo-mdcan.jpeg';

// Import digital font directly in head
const DigitalFontStyle = () => (
  <style dangerouslySetInnerHTML={{
    __html: `
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');
    
    /* Make countdown timer unmissable */
    .countdown-banner {
      font-family: 'Orbitron', monospace !important;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 10000;
      padding: 12px 15px;
      background: linear-gradient(135deg, #008000, #00b300);
      box-shadow: 0 4px 30px rgba(0, 255, 0, 0.4);
      color: #ffffff;
      border-bottom: 3px solid #00ff00;
      text-align: center;
      animation: glow 3s infinite alternate;
    }
    
    /* Sidebar styles */
    .sidebar {
      font-family: 'Orbitron', monospace !important;
      position: fixed;
      left: 0;
      top: 70px; /* Below the header banner */
      bottom: 0;
      width: 250px;
      background: linear-gradient(135deg, #008000, #00b300);
      color: white;
      z-index: 9999;
      padding: 20px;
      box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }
    
    @keyframes glow {
      0% { box-shadow: 0 4px 20px rgba(0, 255, 0, 0.3); }
      100% { box-shadow: 0 4px 30px rgba(0, 255, 0, 0.6); }
    }
    
    .countdown-digits {
      font-family: 'Orbitron', monospace !important;
      letter-spacing: 2px;
      animation: pulse 1.5s infinite alternate;
      background: rgba(0, 0, 0, 0.6);
      padding: 8px 6px;
      border-radius: 8px;
      border: 2px solid rgba(0, 255, 0, 0.5);
      box-shadow: 0 0 15px rgba(0, 255, 0, 0.5) inset;
      min-width: 60px;
      display: inline-block;
      font-size: 28px;
      font-weight: bold;
    }
    
    @keyframes pulse {
      from { text-shadow: 0 0 15px rgba(0, 255, 0, 0.8), 0 0 30px rgba(0, 255, 0, 0.4); }
      to { text-shadow: 0 0 25px rgba(0, 255, 0, 1), 0 0 40px rgba(0, 255, 0, 0.6); }
    }
    
    /* Adjust app for fixed banner and sidebar */
    .App {
      margin-top: 80px;
      margin-left: 250px; /* Make room for sidebar */
      position: relative;
    }
    
    /* Style for the sidebar countdown timer */
    .sidebar-countdown {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 15px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      margin-bottom: 20px;
    }
    
    .sidebar-title {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 15px;
      text-align: center;
      text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }
    
    .sidebar-countdown-digits {
      font-family: 'Orbitron', monospace !important;
      font-size: 24px;
      font-weight: bold;
      margin: 5px 0;
      background: rgba(0, 0, 0, 0.4);
      padding: 10px;
      border-radius: 8px;
      width: 100%;
      text-align: center;
      border: 2px solid rgba(0, 255, 0, 0.3);
      text-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
    }
    
    .sidebar-label {
      font-size: 12px;
      margin-top: 5px;
      text-transform: uppercase;
      opacity: 0.8;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .App {
        margin-left: 0;
      }
      .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
      }
      .sidebar.open {
        transform: translateX(0);
      }
      .sidebar-toggle {
        display: block;
        position: fixed;
        left: 10px;
        top: 85px;
        z-index: 10001;
        background: #008000;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
      }
    }

    /* Slideshow styles */
    .flier-slideshow {
      width: 100%;
      max-width: 900px;
      margin: 20px auto;
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 24px rgba(0,128,0,0.2);
      height: 400px;
    }

    .flier-slideshow img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.7s ease;
    }

    .slideshow-dots {
      position: absolute;
      bottom: 15px;
      left: 0;
      right: 0;
      display: flex;
      justify-content: center;
      gap: 8px;
    }

    .slideshow-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: rgba(255,255,255,0.6);
      border: 1px solid #ccc;
      transition: all 0.3s ease;
    }

    .slideshow-dot.active {
      background: #008000;
      border: 2px solid white;
      transform: scale(1.2);
    }
    `
  }} />
);

function App() {
  const [activeTab, setActiveTab] = useState('registration');
  const [participants, setParticipants] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [userType, setUserType] = useState('participant'); // participant, admin
  const [currentUser, setCurrentUser] = useState(null);
  const [message, setMessage] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % flierImages.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [flierImages.length]);
  
  // Handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
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

  // Define callbacks before they are used in useEffect
  const loadParticipants = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.get('/api/participants');
      setParticipants(data);
    } catch (error) {
      console.error('Error loading participants:', error);
      setMessage('Failed to load participants');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPrograms = useCallback(async () => {
    try {
      const data = await apiService.get('/api/programs');
      setPrograms(data);
    } catch (error) {
      console.error('Error loading programs:', error);
    }
  }, []);

  const loadNotifications = useCallback(async () => {
    try {
      const data = await apiService.get('/api/notifications');
      setNotifications(data);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const data = await apiService.get('/api/stats', {}, false); // Don't cache stats
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }, []);

  // Load initial data
  useEffect(() => {
    if (userType === 'admin') {
      loadParticipants();
      loadPrograms();
      loadNotifications();
      loadStats();
    }
  }, [userType, loadParticipants, loadPrograms, loadNotifications, loadStats]);

  // Auto-refresh data every 30 seconds for admin
  useEffect(() => {
    if (userType === 'admin') {
      const interval = setInterval(() => {
        loadStats();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [userType, loadStats]);

  const handleParticipantAdded = useCallback((newParticipant) => {
    setParticipants(prev => [newParticipant, ...prev]);
    loadStats();
  }, [loadStats]);

  const handleBulkUpload = useCallback(() => {
    loadParticipants();
    loadStats();
  }, [loadParticipants, loadStats]);

  const handleProgramAdded = useCallback((newProgram) => {
    setPrograms(prev => [newProgram, ...prev]);
  }, []);

  const handleNotificationSent = useCallback(() => {
    loadNotifications();
  }, [loadNotifications]);

  const loginAsParticipant = useCallback(async (email) => {
    try {
      const data = await apiService.get(`/api/participants/${email}/dashboard`);
      setCurrentUser(data.participant);
      setUserType('participant');
      setActiveTab('dashboard');
    } catch (error) {
      setMessage('Participant not found. Please register first.');
    }
  }, []);

  const switchToAdmin = useCallback(() => {
    setUserType('admin');
    setCurrentUser(null);
    setActiveTab('admin-dashboard');
  }, []);

  const switchToParticipant = useCallback(() => {
    setUserType('participant');
    setCurrentUser(null);
    setActiveTab('registration');
  }, []);

  // Legacy functions for backward compatibility
  const addParticipant = useCallback(async (participantData) => {
    try {
      setLoading(true);
      const data = await apiService.post('/api/participants', participantData);
      setParticipants(prev => [...prev, data]);
      setMessage('Participant added successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error adding participant:', error);
      setMessage('Error adding participant. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const sendCertificate = useCallback(async (participantId) => {
    try {
      setLoading(true);
      await apiService.post(`/api/send-certificate/${participantId}`);
      setMessage('Certificate sent successfully!');
      loadParticipants(); // Refresh list to update status
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error sending certificate:', error);
      setMessage('Error sending certificate. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [loadParticipants]);

  const sendAllCertificates = useCallback(async () => {
    try {
      setLoading(true);
      await apiService.post('/api/send-all-certificates');
      setMessage('All certificates sent successfully!');
      loadParticipants(); // Refresh list to update statuses
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error sending certificates:', error);
      setMessage('Error sending certificates. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [loadParticipants]);

  return (
    <div className="App">
      <DigitalFontStyle />
      
      {/* Green Banner - Always visible */}
      <div className="countdown-banner">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: '15px'
        }}>
          <img 
            src={mdcanLogo} 
            alt="MDCAN Logo" 
            style={{ 
              height: '40px', 
              marginRight: '10px',
              borderRadius: '5px',
              border: '2px solid rgba(255,255,255,0.7)'
            }} 
          />
          <div style={{ 
            fontSize: '22px', 
            fontWeight: 'bold',
            textShadow: '0 0 15px rgba(255, 255, 255, 0.7)',
            whiteSpace: 'nowrap',
            marginRight: '5px'
          }}>
            🏥 MDCAN 14th BDM - ENUGU 2025
          </div>
        </div>
      </div>
      
      {/* Sidebar with Countdown Timer */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-countdown">
          <div className="sidebar-title">⏱️ CONFERENCE COUNTDOWN</div>
          
          <div className="sidebar-countdown-digits">
            {timeRemaining.days.toString().padStart(2, '0')}
            <div className="sidebar-label">DAYS</div>
          </div>
          
          <div className="sidebar-countdown-digits">
            {timeRemaining.hours.toString().padStart(2, '0')}
            <div className="sidebar-label">HOURS</div>
          </div>
          
          <div className="sidebar-countdown-digits">
            {timeRemaining.minutes.toString().padStart(2, '0')}
            <div className="sidebar-label">MINUTES</div>
          </div>
          
          <div className="sidebar-countdown-digits">
            {timeRemaining.seconds.toString().padStart(2, '0')}
            <div className="sidebar-label">SECONDS</div>
          </div>
        </div>
        
        {/* Additional sidebar content can go here */}
        <div style={{ padding: '10px 0', borderBottom: '1px solid rgba(255, 255, 255, 0.2)', marginBottom: '15px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>Quick Links</h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ marginBottom: '8px' }}>📝 Registration</li>
            <li style={{ marginBottom: '8px' }}>📊 My Dashboard</li>
            <li style={{ marginBottom: '8px' }}>📅 Program Schedule</li>
            <li style={{ marginBottom: '8px' }}>🏆 Certificates</li>
          </ul>
        </div>
      </div>
      
      {/* Mobile sidebar toggle button */}
      <button 
        className="sidebar-toggle" 
        style={{ display: windowWidth <= 768 ? 'block' : 'none' }}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? '×' : '☰'}
      </button>
      
      {/* Main Content */}
      <main className="app-main">
        {loading && <div className="loading-spinner">Loading...</div>}
        
        {/* Flier Slideshow */}
        <div className="flier-slideshow">
          <img
            src={flierImages[currentSlide]}
            alt={`Conference Flier ${currentSlide + 1}`}
          />
          <div className="slideshow-dots">
            {flierImages.map((_, idx) => (
              <div 
                key={idx} 
                className={`slideshow-dot ${idx === currentSlide ? 'active' : ''}`}
                onClick={() => setCurrentSlide(idx)}
              />
            ))}
          </div>
        </div>
      
        {/* Offline indicator */}
        {!isOnline && (
          <div className="alert alert-warning" style={{margin: 0, borderRadius: 0}}>
            🌐 You are currently offline. Some features may not be available.
          </div>
        )}

      {/* Modern Header */}
      <header className="header">
        <div className="container">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <img src={mdcanLogo} alt="MDCAN Logo" style={{ width: '48px', height: '48px', borderRadius: '8px' }} />
              <div>
                <h1 className="text-xl font-bold text-white mb-0">MDCAN 14th Biennial Delegates' Meeting</h1>
                <p className="text-sm opacity-90 mb-0">and SCIENTIFIC Conference • Enugu • September 1-6, 2025</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex bg-white bg-opacity-20 rounded-lg p-1">
                <button 
                  className={`btn btn-sm ${userType === 'participant' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={switchToParticipant}
                >
                  👤 Participant
                </button>
                <button 
                  className={`btn btn-sm ${userType === 'admin' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={switchToAdmin}
                >
                  🛠️ Admin
                </button>
              </div>
              
              {userType === 'participant' && !currentUser && (
                <button 
                  onClick={() => {
                    const email = prompt('Enter your email to access your dashboard:');
                    if (email) loginAsParticipant(email);
                  }}
                  className="btn btn-secondary btn-sm"
                >
                  📋 My Dashboard
                </button>
              )}
              
              {currentUser && (
                <div className="flex items-center gap-2 text-white">
                  <span className="text-sm">Welcome, {currentUser.name}</span>
                  <button onClick={switchToParticipant} className="btn btn-sm btn-outline">Logout</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Modern Navigation */}
      <nav className="nav">
        <div className="container">
          <div className="nav-container">
            <div className="flex items-center gap-2">
              <button 
                className="nav-toggle btn btn-sm btn-outline md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                ☰
              </button>
              
              {/* Statistics for admin */}
              {userType === 'admin' && stats.total_participants && (
                <div className="flex items-center gap-4 text-sm">
                  <span className="status status-info">
                    👥 {stats.total_participants} Participants
                  </span>
                  <span className="status status-success">
                    📜 {stats.certificates_sent || 0} Certificates Sent
                  </span>
                  {stats.upcoming_programs && (
                    <span className="status status-warning">
                      📅 {stats.upcoming_programs} Upcoming Programs
                    </span>
                  )}
                </div>
              )}
            </div>
            
            <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
              {userType === 'participant' ? (
                // Participant Navigation
                <>
                  <button 
                    className={`nav-link ${activeTab === 'registration' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('registration'); setMobileMenuOpen(false);}}
                  >
                    📝 Register
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'schedule' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('schedule'); setMobileMenuOpen(false);}}
                  >
                    📅 Schedule
                  </button>
                  {currentUser && (
                    <button 
                      className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
                      onClick={() => {setActiveTab('dashboard'); setMobileMenuOpen(false);}}
                    >
                      📊 My Dashboard
                    </button>
                  )}
                  <button 
                    className={`nav-link ${activeTab === 'certificates' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('certificates'); setMobileMenuOpen(false);}}
                  >
                    🏆 Certificates
                  </button>
                </>
              ) : (
                // Admin Navigation
                <>
                  <button 
                    className={`nav-link ${activeTab === 'admin-dashboard' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('admin-dashboard'); setMobileMenuOpen(false);}}
                  >
                    📊 Dashboard
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'participants' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('participants'); setMobileMenuOpen(false);}}
                  >
                    👥 Participants
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'bulk-upload' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('bulk-upload'); setMobileMenuOpen(false);}}
                  >
                    📤 Bulk Upload
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'notifications' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('notifications'); setMobileMenuOpen(false);}}
                  >
                    🔔 Notifications
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'attendance' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('attendance'); setMobileMenuOpen(false);}}
                  >
                    ✅ Attendance
                  </button>
                  <button 
                    className={`nav-link ${activeTab === 'certificate-preview' ? 'active' : ''}`}
                    onClick={() => {setActiveTab('certificate-preview'); setMobileMenuOpen(false);}}
                  >
                    🏆 Preview
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Message Display */}
      {message && (
        <div className={`alert ${message.includes('Error') || message.includes('Failed') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {/* Statistics Bar (Admin only) */}
      {userType === 'admin' && stats.participants && (
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
                  setMessage('Registration successful! Welcome to MDCAN 14th Biennial Delegates\' Meeting and SCIENTIFIC Conference 2025.');
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
        {userType === 'admin' && (
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
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>MDCAN 14th Biennial Delegates' Meeting and SCIENTIFIC Conference</h4>
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
            <p><strong>Prof. Appolos Ndukuba</strong><br />LOC Chairman</p>
            <p><strong>Dr. Augustine Duru</strong><br />LOC Secretary<br/>MDCAN Sec. Gen.</p>
          </div>
          
          <div className="footer-section">
            <h4>Platform Status</h4>
            <p>🟢 Online & Operational</p>
            <p>🔒 Secure Registration</p>
            <p>📧 Email Notifications Active</p>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 MDCAN 14th Biennial Delegates' Meeting and SCIENTIFIC Conference. All rights reserved. | Certificate Generation Platform v2.0</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
