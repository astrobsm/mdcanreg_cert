import React, { useState } from 'react';
import axios from 'axios';

const NotificationCenter = ({ notifications, programs, onNotificationSent }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [newNotification, setNewNotification] = useState({
    title: '',
    message: '',
    notification_type: 'general_announcement',
    target_audience: 'all',
    target_program_id: '',
    scheduled_time: '',
    send_email: true,
    send_push: true,
    send_sms: false
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewNotification(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleCreateNotification = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Set scheduled time to now if not specified
      const notificationData = {
        ...newNotification,
        scheduled_time: newNotification.scheduled_time || new Date().toISOString()
      };
      
      await axios.post('/api/notifications', notificationData);
      
      setMessage('✅ Notification created and sent successfully!');
      
      // Reset form
      setNewNotification({
        title: '',
        message: '',
        notification_type: 'general_announcement',
        target_audience: 'all',
        target_program_id: '',
        scheduled_time: '',
        send_email: true,
        send_push: true,
        send_sms: false
      });
      
      setShowCreateForm(false);
      
      if (onNotificationSent) {
        onNotificationSent();
      }
      
      setTimeout(() => setMessage(''), 5000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to create notification';
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const sendNotificationNow = async (notificationId) => {
    try {
      setLoading(true);
      const response = await axios.post(`/api/notifications/${notificationId}/send`);
      
      setMessage(`✅ Notification sent! ${response.data.statistics.total_recipients} recipients reached.`);
      
      if (onNotificationSent) {
        onNotificationSent();
      }
      
      setTimeout(() => setMessage(''), 5000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to send notification';
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateTime) => {
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

  const getNotificationTypeIcon = (type) => {
    switch (type) {
      case 'program_reminder': return '⏰';
      case 'general_announcement': return '📢';
      case 'emergency': return '🚨';
      case 'welcome': return '👋';
      case 'certificate_ready': return '🏆';
      default: return '🔔';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'sent': return 'green';
      case 'scheduled': return 'blue';
      case 'failed': return 'red';
      case 'cancelled': return 'gray';
      default: return 'orange';
    }
  };

  // Quick notification templates
  const quickTemplates = [
    {
      title: 'Conference Welcome',
      message: `
        <div class="highlight">
          <strong>Welcome to MDCAN BDM 14th - 2025!</strong>
        </div>
        
        <p>We're excited to have you join us for this prestigious conference in Enugu from September 1-6, 2025.</p>
        
        <p><strong>Important Reminders:</strong></p>
        <ul>
          <li>Check your email regularly for program updates</li>
          <li>Register for sessions that require advance registration</li>
          <li>Review the conference schedule in your dashboard</li>
          <li>Ensure you have our contact information for emergencies</li>
        </ul>
        
        <p>Looking forward to an enriching conference experience!</p>
      `,
      type: 'welcome',
      audience: 'all'
    },
    {
      title: 'Session Reminder Template',
      message: `
        <div class="highlight">
          <strong>Session Starting Soon</strong>
        </div>
        
        <p>This is a reminder that your registered session is starting in 30 minutes:</p>
        
        <p><strong>[Session Title will be auto-filled]</strong><br>
        <strong>Time:</strong> [Time will be auto-filled]<br>
        <strong>Venue:</strong> [Venue will be auto-filled]</p>
        
        <p>Please arrive on time and bring any required materials.</p>
      `,
      type: 'program_reminder',
      audience: 'specific_program'
    },
    {
      title: 'Certificates Available',
      message: `
        <div class="highlight">
          <strong>Your Certificate is Ready!</strong>
        </div>
        
        <p>Congratulations on completing the MDCAN BDM 14th - 2025 conference!</p>
        
        <p>Your certificate is now available for download in your participant dashboard.</p>
        
        <p>To download your certificate:</p>
        <ol>
          <li>Login to your participant dashboard</li>
          <li>Go to the "Certificate" section</li>
          <li>Click "Download Certificate"</li>
        </ol>
        
        <p>Thank you for your participation and we hope to see you at future events!</p>
      `,
      type: 'certificate_ready',
      audience: 'participants'
    }
  ];

  const applyTemplate = (template) => {
    setNewNotification(prev => ({
      ...prev,
      title: template.title,
      message: template.message,
      notification_type: template.type,
      target_audience: template.audience
    }));
    setShowCreateForm(true);
  };

  return (
    <div className="notification-center">
      <div className="center-header">
        <h2>🔔 Notification Center</h2>
        <p>Send notifications and announcements to conference participants</p>
        
        <div className="header-actions">
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-primary"
          >
            {showCreateForm ? '❌ Cancel' : '➕ Create Notification'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Quick Templates */}
      {!showCreateForm && (
        <div className="quick-templates">
          <h3>🚀 Quick Templates</h3>
          <div className="templates-grid">
            {quickTemplates.map((template, index) => (
              <div key={index} className="template-card">
                <h4>{getNotificationTypeIcon(template.type)} {template.title}</h4>
                <p>Target: {template.audience}</p>
                <p>Type: {template.type.replace('_', ' ')}</p>
                <button 
                  onClick={() => {
                    applyTemplate(template);
                  }}
                  className="btn-outline"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Notification Form */}
      {showCreateForm && (
        <form onSubmit={handleCreateNotification} className="create-notification-form">
          <h3>➕ Create New Notification</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Notification Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={newNotification.title}
                onChange={handleInputChange}
                required
                placeholder="Enter notification title"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="notification_type">Type *</label>
              <select
                id="notification_type"
                name="notification_type"
                value={newNotification.notification_type}
                onChange={handleInputChange}
                required
              >
                <option value="general_announcement">General Announcement</option>
                <option value="program_reminder">Program Reminder</option>
                <option value="welcome">Welcome Message</option>
                <option value="certificate_ready">Certificate Ready</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="message">Message Content *</label>
            <textarea
              id="message"
              name="message"
              value={newNotification.message}
              onChange={handleInputChange}
              required
              rows="8"
              placeholder="Enter notification message (HTML supported)"
            />
            <small>Tip: You can use HTML tags for formatting (e.g., &lt;strong&gt;, &lt;em&gt;, &lt;ul&gt;, &lt;li&gt;)</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="target_audience">Target Audience *</label>
              <select
                id="target_audience"
                name="target_audience"
                value={newNotification.target_audience}
                onChange={handleInputChange}
                required
              >
                <option value="all">All Participants</option>
                <option value="participants">Conference Participants</option>
                <option value="speakers">Speakers</option>
                <option value="organizers">Organizers</option>
                <option value="specific_program">Specific Program Attendees</option>
              </select>
            </div>
            
            {newNotification.target_audience === 'specific_program' && (
              <div className="form-group">
                <label htmlFor="target_program_id">Target Program</label>
                <select
                  id="target_program_id"
                  name="target_program_id"
                  value={newNotification.target_program_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a program</option>
                  {programs.map(program => (
                    <option key={program.id} value={program.id}>
                      {program.title} - {formatDateTime(program.start_time)}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="scheduled_time">Schedule Time (leave empty for immediate)</label>
            <input
              type="datetime-local"
              id="scheduled_time"
              name="scheduled_time"
              value={newNotification.scheduled_time}
              onChange={handleInputChange}
            />
            <small>Leave empty to send immediately, or set a future time for scheduled delivery</small>
          </div>

          <div className="delivery-options">
            <h4>📡 Delivery Channels</h4>
            <div className="checkbox-group">
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="send_email"
                  name="send_email"
                  checked={newNotification.send_email}
                  onChange={handleInputChange}
                />
                <label htmlFor="send_email">📧 Email Notifications</label>
              </div>
              
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="send_push"
                  name="send_push"
                  checked={newNotification.send_push}
                  onChange={handleInputChange}
                />
                <label htmlFor="send_push">🔔 Push Notifications</label>
              </div>
              
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="send_sms"
                  name="send_sms"
                  checked={newNotification.send_sms}
                  onChange={handleInputChange}
                />
                <label htmlFor="send_sms">📱 SMS Notifications</label>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={() => setShowCreateForm(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Creating...' : '🚀 Create & Send Notification'}
            </button>
          </div>
        </form>
      )}

      {/* Notifications History */}
      <div className="notifications-history">
        <h3>📋 Recent Notifications</h3>
        
        {notifications && notifications.length === 0 ? (
          <div className="empty-state">
            <h4>📭 No Notifications Yet</h4>
            <p>Create your first notification to communicate with participants.</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications && notifications.slice(0, 10).map(notification => (
              <div key={notification.id} className="notification-card">
                <div className="notification-header">
                  <div className="notification-meta">
                    <span className="notification-type">
                      {getNotificationTypeIcon(notification.notification_type)} {notification.notification_type.replace('_', ' ')}
                    </span>
                    <span className={`status-badge ${getStatusColor(notification.status)}`}>
                      {notification.status}
                    </span>
                  </div>
                  
                  <div className="notification-actions">
                    {notification.status === 'scheduled' && (
                      <button 
                        onClick={() => sendNotificationNow(notification.id)}
                        disabled={loading}
                        className="btn-sm btn-primary"
                      >
                        Send Now
                      </button>
                    )}
                  </div>
                </div>
                
                <h4 className="notification-title">{notification.title}</h4>
                
                <div className="notification-preview">
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: notification.message.length > 200 
                        ? notification.message.substring(0, 200) + '...' 
                        : notification.message 
                    }}
                  />
                </div>
                
                <div className="notification-details">
                  <div className="detail-row">
                    <span><strong>Target:</strong> {notification.target_audience}</span>
                    {notification.program_title && (
                      <span><strong>Program:</strong> {notification.program_title}</span>
                    )}
                  </div>
                  
                  <div className="detail-row">
                    <span><strong>Scheduled:</strong> {formatDateTime(notification.scheduled_time)}</span>
                    {notification.sent_at && (
                      <span><strong>Sent:</strong> {formatDateTime(notification.sent_at)}</span>
                    )}
                  </div>
                  
                  <div className="delivery-channels">
                    <strong>Channels:</strong>
                    {notification.send_email && <span className="channel">📧 Email</span>}
                    {notification.send_push && <span className="channel">🔔 Push</span>}
                    {notification.send_sms && <span className="channel">📱 SMS</span>}
                  </div>
                  
                  {notification.delivery_stats && Object.keys(notification.delivery_stats).length > 0 && (
                    <div className="delivery-stats">
                      <strong>Delivery Stats:</strong>
                      <span>📧 {notification.delivery_stats.email_sent || 0} sent</span>
                      <span>🔔 {notification.delivery_stats.push_sent || 0} pushed</span>
                      <span>👥 {notification.delivery_stats.total_recipients || 0} total</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationCenter;
