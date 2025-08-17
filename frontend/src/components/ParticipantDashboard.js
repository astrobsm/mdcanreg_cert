import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ParticipantDashboard = ({ participantEmail, onDataUpdate }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [activeSection, setActiveSection] = useState('overview');

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [participantEmail]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/participants/${participantEmail}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setMessage('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const downloadCertificate = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/participants/${participantEmail}/certificate`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const fileName = dashboardData?.participant?.name 
        ? `MDCAN_BDM_2025_Certificate_${dashboardData.participant.name.replace(/ /g, '_')}.pdf`
        : 'MDCAN_BDM_2025_Certificate.pdf';
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setMessage('Certificate downloaded successfully!');
      setTimeout(() => setMessage(''), 3000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Certificate download failed';
      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const previewCertificate = async () => {
    try {
      const response = await axios.get(`/api/participants/${participantEmail}/certificate/preview`, {
        responseType: 'blob'
      });
      
      // Open in new tab
      const url = window.URL.createObjectURL(new Blob([response.data]));
      window.open(url, '_blank');
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      setMessage('Certificate preview failed');
    }
  };

  const formatDateTime = (dateTime) => {
    if (!dateTime) return 'Not set';
    return new Date(dateTime).toLocaleString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'green';
      case 'registered': return 'blue';
      case 'attended': return 'purple';
      case 'pending': return 'orange';
      case 'sent': return 'green';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  if (loading && !dashboardData) {
    return <div className="loading-spinner">Loading your dashboard...</div>;
  }

  if (loading) {
    return (
      <div className="loading-state">
        <h3>🔄 Loading Dashboard...</h3>
        <p>Please wait while we load your conference information.</p>
      </div>
    );
  }

  if (!dashboardData || !dashboardData.participant) {
    return (
      <div className="error-state">
        <h3>⚠️ Dashboard Unavailable</h3>
        <p>Unable to load your dashboard. Please try again later.</p>
        {message && <p className="error">{message}</p>}
        <button onClick={loadDashboardData} className="retry-btn">
          🔄 Retry
        </button>
      </div>
    );
  }

  const { participant, registered_sessions, upcoming_programs, recent_notifications, statistics } = dashboardData;

  return (
    <div className="participant-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h2>👋 Welcome, {participant?.name || 'Participant'}!</h2>
          <p>Your MDCAN BDM 2025 Conference Dashboard</p>
        </div>
        
        <div className="registration-info">
          <div className="info-card">
            <h4>Registration Status</h4>
            <span className={`status-badge ${getStatusColor(participant.registration_status)}`}>
              {participant.registration_status}
            </span>
          </div>
          
          <div className="info-card">
            <h4>Registration #</h4>
            <span className="registration-number">{participant.certificate_number}</span>
          </div>
        </div>
      </div>

      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Navigation */}
      <div className="dashboard-nav">
        <button 
          className={activeSection === 'overview' ? 'active' : ''}
          onClick={() => setActiveSection('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={activeSection === 'sessions' ? 'active' : ''}
          onClick={() => setActiveSection('sessions')}
        >
          📅 My Sessions
        </button>
        <button 
          className={activeSection === 'notifications' ? 'active' : ''}
          onClick={() => setActiveSection('notifications')}
        >
          🔔 Notifications
        </button>
        <button 
          className={activeSection === 'certificate' ? 'active' : ''}
          onClick={() => setActiveSection('certificate')}
        >
          🏆 Certificate
        </button>
        <button 
          className={activeSection === 'profile' ? 'active' : ''}
          onClick={() => setActiveSection('profile')}
        >
          👤 Profile
        </button>
      </div>

      {/* Content */}
      <div className="dashboard-content">
        
        {/* Overview */}
        {activeSection === 'overview' && (
          <div className="overview-section">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{statistics.total_registered_sessions}</h3>
                <p>Sessions Registered</p>
                <span className="icon">📝</span>
              </div>
              
              <div className="stat-card">
                <h3>{statistics.attended_sessions}</h3>
                <p>Sessions Attended</p>
                <span className="icon">✅</span>
              </div>
              
              <div className="stat-card">
                <h3>{upcoming_programs.length}</h3>
                <p>Upcoming Programs</p>
                <span className="icon">⏰</span>
              </div>
              
              <div className="stat-card">
                <h3>{statistics.certificate_status}</h3>
                <p>Certificate Status</p>
                <span className="icon">🏆</span>
              </div>
            </div>

            {/* Upcoming Programs */}
            {upcoming_programs.length > 0 && (
              <div className="upcoming-section">
                <h3>⏰ Upcoming Programs (Next 24 Hours)</h3>
                <div className="programs-list">
                  {upcoming_programs.slice(0, 3).map(program => (
                    <div key={program.id} className="program-card mini">
                      <div className="program-info">
                        <h4>{program.title}</h4>
                        <p>📅 {formatDateTime(program.start_time)}</p>
                        {program.venue && <p>📍 {program.venue}</p>}
                      </div>
                      {program.is_mandatory && (
                        <span className="mandatory-badge">⚠️ Mandatory</span>
                      )}
                    </div>
                  ))}
                </div>
                
                {upcoming_programs.length > 3 && (
                  <button 
                    onClick={() => setActiveSection('sessions')}
                    className="btn-outline"
                  >
                    View All Sessions →
                  </button>
                )}
              </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions">
              <h3>🚀 Quick Actions</h3>
              <div className="actions-grid">
                <button 
                  onClick={() => setActiveSection('sessions')}
                  className="action-btn"
                >
                  📅 View My Sessions
                </button>
                
                <button 
                  onClick={() => setActiveSection('certificate')}
                  className="action-btn"
                >
                  🏆 Check Certificate
                </button>
                
                <button 
                  onClick={() => setActiveSection('profile')}
                  className="action-btn"
                >
                  👤 Update Profile
                </button>
                
                <button 
                  onClick={loadDashboardData}
                  className="action-btn"
                >
                  🔄 Refresh Data
                </button>
              </div>
            </div>
          </div>
        )}

        {/* My Sessions */}
        {activeSection === 'sessions' && (
          <div className="sessions-section">
            <h3>📅 My Registered Sessions</h3>
            
            {registered_sessions.length === 0 ? (
              <div className="empty-state">
                <h4>📝 No Sessions Registered</h4>
                <p>You haven't registered for any sessions yet.</p>
                <button 
                  onClick={() => window.location.href = '#schedule'} 
                  className="btn-primary"
                >
                  Browse Available Sessions
                </button>
              </div>
            ) : (
              <div className="sessions-list">
                {registered_sessions.map(({ registration, program }) => (
                  <div key={registration.id} className="session-card">
                    <div className="session-header">
                      <h4>{program.title}</h4>
                      <span className={`status-badge ${getStatusColor(registration.attendance_status)}`}>
                        {registration.attendance_status}
                      </span>
                    </div>
                    
                    <div className="session-details">
                      <p>📅 {formatDateTime(program.start_time)} - {new Date(program.end_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}</p>
                      {program.venue && <p>📍 {program.venue}</p>}
                      {program.speaker_name && <p>🎤 {program.speaker_name}</p>}
                    </div>
                    
                    {program.description && (
                      <p className="session-description">{program.description}</p>
                    )}
                    
                    <div className="session-meta">
                      <small>Registered: {formatDateTime(registration.registered_at)}</small>
                      {registration.rating && (
                        <div className="rating">
                          Rating: {'⭐'.repeat(registration.rating)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Notifications */}
        {activeSection === 'notifications' && (
          <div className="notifications-section">
            <h3>🔔 Recent Notifications</h3>
            
            {recent_notifications.length === 0 ? (
              <div className="empty-state">
                <h4>🔔 No Recent Notifications</h4>
                <p>You'll receive updates about the conference here.</p>
              </div>
            ) : (
              <div className="notifications-list">
                {recent_notifications.map(notification => (
                  <div key={notification.id} className="notification-card">
                    <div className="notification-header">
                      <h4>{notification.title}</h4>
                      <span className="notification-time">
                        {formatDateTime(notification.created_at)}
                      </span>
                    </div>
                    
                    <div 
                      className="notification-message"
                      dangerouslySetInnerHTML={{ __html: notification.message }}
                    />
                    
                    <div className="notification-meta">
                      <span className="notification-type">{notification.notification_type}</span>
                      {notification.program_title && (
                        <span className="related-program">Related: {notification.program_title}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Certificate */}
        {activeSection === 'certificate' && (
          <div className="certificate-section">
            <h3>🏆 Your Certificate</h3>
            
            <div className="certificate-info">
              <div className="certificate-details">
                <h4>Certificate Information</h4>
                <div className="details-grid">
                  <div className="detail-item">
                    <strong>Type:</strong> 
                    <span>{participant.certificate_type === 'participation' ? 'Certificate of Participation' : 'Acknowledgement of Service'}</span>
                  </div>
                  
                  <div className="detail-item">
                    <strong>Status:</strong>
                    <span className={`status-badge ${getStatusColor(participant.certificate_status)}`}>
                      {participant.certificate_status}
                    </span>
                  </div>
                  
                  <div className="detail-item">
                    <strong>Certificate Number:</strong>
                    <span>{participant.certificate_number}</span>
                  </div>
                  
                  {participant.certificate_sent_at && (
                    <div className="detail-item">
                      <strong>Sent Date:</strong>
                      <span>{formatDateTime(participant.certificate_sent_at)}</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="certificate-actions">
                <button 
                  onClick={previewCertificate}
                  className="btn-secondary"
                  disabled={loading}
                >
                  👁️ Preview Certificate
                </button>
                
                {(participant.registration_status === 'attended' || participant.event_attendance) && (
                  <button 
                    onClick={downloadCertificate}
                    className="btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Downloading...' : '📥 Download Certificate'}
                  </button>
                )}
                
                {participant.registration_status !== 'attended' && !participant.event_attendance && (
                  <div className="certificate-notice">
                    <p>🔒 Certificate will be available after conference attendance is confirmed.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Profile */}
        {activeSection === 'profile' && (
          <div className="profile-section">
            <h3>👤 My Profile</h3>
            
            <div className="profile-info">
              <div className="info-grid">
                <div className="info-item">
                  <strong>Name:</strong>
                  <span>{participant?.name || 'Not provided'}</span>
                </div>
                
                <div className="info-item">
                  <strong>Email:</strong>
                  <span>{participant.email}</span>
                </div>
                
                <div className="info-item">
                  <strong>Phone:</strong>
                  <span>{participant.phone_number || 'Not provided'}</span>
                </div>
                
                <div className="info-item">
                  <strong>Organization:</strong>
                  <span>{participant.organization || 'Not provided'}</span>
                </div>
                
                <div className="info-item">
                  <strong>Position:</strong>
                  <span>{participant.position || 'Not provided'}</span>
                </div>
                
                <div className="info-item">
                  <strong>Registration Type:</strong>
                  <span>{participant.registration_type}</span>
                </div>
                
                <div className="info-item">
                  <strong>Registered:</strong>
                  <span>{formatDateTime(participant.created_at)}</span>
                </div>
              </div>
              
              <div className="notification-preferences">
                <h4>📧 Notification Preferences</h4>
                <div className="preferences-list">
                  <div className="preference-item">
                    <span>Email Notifications:</span>
                    <span className={participant.email_notifications ? 'enabled' : 'disabled'}>
                      {participant.email_notifications ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                  </div>
                  
                  <div className="preference-item">
                    <span>SMS Notifications:</span>
                    <span className={participant.sms_notifications ? 'enabled' : 'disabled'}>
                      {participant.sms_notifications ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                  </div>
                  
                  <div className="preference-item">
                    <span>Push Notifications:</span>
                    <span className={participant.push_notifications ? 'enabled' : 'disabled'}>
                      {participant.push_notifications ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                  </div>
                </div>
              </div>
              
              {(participant.dietary_requirements || participant.special_needs) && (
                <div className="additional-info">
                  <h4>📋 Additional Information</h4>
                  
                  {participant.dietary_requirements && (
                    <div className="info-item">
                      <strong>Dietary Requirements:</strong>
                      <p>{participant.dietary_requirements}</p>
                    </div>
                  )}
                  
                  {participant.special_needs && (
                    <div className="info-item">
                      <strong>Special Needs:</strong>
                      <p>{participant.special_needs}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParticipantDashboard;
