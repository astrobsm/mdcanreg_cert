import React, { useState } from 'react';
import axios from 'axios';

const AdminDashboard = ({ stats, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [actionLoading, setActionLoading] = useState({});

  const handleBulkCertificateGeneration = async () => {
    try {
      setActionLoading({ certificates: true });
      const response = await axios.post('/api/certificates/bulk-generate');
      setMessage(`✅ ${response.data.message}`);
      if (onRefresh) onRefresh();
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      setMessage(`❌ ${error.response?.data?.error || 'Bulk certificate generation failed'}`);
    } finally {
      setActionLoading({ certificates: false });
    }
  };

  const handleSendAllCertificates = async () => {
    try {
      setActionLoading({ sendAll: true });
      const response = await axios.post('/api/send-all-certificates');
      setMessage(`✅ ${response.data.message}`);
      if (onRefresh) onRefresh();
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      setMessage(`❌ ${error.response?.data?.error || 'Failed to send certificates'}`);
    } finally {
      setActionLoading({ sendAll: false });
    }
  };

  const exportData = async (format) => {
    try {
      setActionLoading({ [`export_${format}`]: true });
      const response = await axios.get(`/api/reports/export/${format}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `mdcan_bdm_2025_report.${format === 'excel' ? 'xlsx' : 'csv'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setMessage(`✅ ${format.toUpperCase()} report downloaded successfully!`);
      setTimeout(() => setMessage(''), 3000);
      
    } catch (error) {
      setMessage(`❌ Export failed: ${error.response?.data?.error || 'Unknown error'}`);
    } finally {
      setActionLoading({ [`export_${format}`]: false });
    }
  };

  const getConferenceSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/conference-summary');
      
      // Display summary in a modal or new window
      const summaryWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
      summaryWindow.document.write(`
        <html>
          <head>
            <title>MDCAN BDM 2025 - Conference Summary</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .summary-section { margin-bottom: 30px; }
              .summary-section h2 { color: #1a365d; border-bottom: 2px solid #d4af37; }
              .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
              .stat-item { background: #f5f5f5; padding: 15px; border-radius: 8px; }
              .stat-value { font-size: 24px; font-weight: bold; color: #d4af37; }
              table { width: 100%; border-collapse: collapse; margin-top: 10px; }
              th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
              th { background-color: #f2f2f2; }
            </style>
          </head>
          <body>
            <h1>MDCAN BDM 14th - 2025 Conference Summary</h1>
            <div class="summary-section">
              <h2>Participants Overview</h2>
              <div class="stat-grid">
                <div class="stat-item">
                  <div class="stat-value">${response.data.participants.total}</div>
                  <div>Total Participants</div>
                </div>
                ${Object.entries(response.data.participants.by_type || {}).map(([type, count]) => `
                  <div class="stat-item">
                    <div class="stat-value">${count}</div>
                    <div>${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                  </div>
                `).join('')}
              </div>
            </div>
            
            <div class="summary-section">
              <h2>Programs & Sessions</h2>
              <div class="stat-grid">
                <div class="stat-item">
                  <div class="stat-value">${response.data.programs.total}</div>
                  <div>Total Programs</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">${response.data.sessions.total_registrations}</div>
                  <div>Session Registrations</div>
                </div>
              </div>
            </div>
            
            ${(response.data.feedback.top_rated_sessions || []).length > 0 ? `
              <div class="summary-section">
                <h2>Top Rated Sessions</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Session Title</th>
                      <th>Average Rating</th>
                      <th>Total Ratings</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${(response.data.feedback.top_rated_sessions || []).map(session => `
                      <tr>
                        <td>${session.title}</td>
                        <td>${session.average_rating.toFixed(1)} ⭐</td>
                        <td>${session.rating_count}</td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            ` : ''}
            
            <div class="summary-section">
              <h2>Certificate Status</h2>
              <div class="stat-grid">
                ${Object.entries(response.data.certificates.by_status || {}).map(([status, count]) => `
                  <div class="stat-item">
                    <div class="stat-value">${count}</div>
                    <div>${status.charAt(0).toUpperCase() + status.slice(1)}</div>
                  </div>
                `).join('')}
              </div>
            </div>
            
            <p><em>Generated on ${new Date().toLocaleString()}</em></p>
          </body>
        </html>
      `);
      
    } catch (error) {
      setMessage(`❌ Failed to generate summary: ${error.response?.data?.error || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h2>🛠️ Admin Dashboard</h2>
        <p>MDCAN BDM 2025 Conference Management</p>
        
        <div className="header-actions">
          <button onClick={onRefresh} className="btn-secondary" disabled={loading}>
            🔄 Refresh Data
          </button>
          <button onClick={getConferenceSummary} className="btn-outline" disabled={loading}>
            📊 View Full Summary
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Quick Stats */}
      {stats.participants && (
        <div className="quick-stats">
          <div className="stats-grid">
            <div className="stat-card primary">
              <h3>{stats.participants.total}</h3>
              <p>Total Participants</p>
              <span className="icon">👥</span>
            </div>
            
            <div className="stat-card success">
              <h3>{stats.participants.certificates_sent}</h3>
              <p>Certificates Sent</p>
              <span className="icon">✅</span>
            </div>
            
            <div className="stat-card warning">
              <h3>{stats.participants.certificates_pending}</h3>
              <p>Certificates Pending</p>
              <span className="icon">⏳</span>
            </div>
            
            <div className="stat-card info">
              <h3>{stats.recent_activity?.registrations_today || 0}</h3>
              <p>Registered Today</p>
              <span className="icon">📅</span>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Statistics */}
      {stats.participants && (
        <div className="detailed-stats">
          <div className="stats-section">
            <h3>📋 Registration Statistics</h3>
            <div className="stats-breakdown">
              <div className="breakdown-item">
                <span className="label">Participation Certificates:</span>
                <span className="value">{stats.participants.participation_certificates}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Service Certificates:</span>
                <span className="value">{stats.participants.service_certificates}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Failed Certificates:</span>
                <span className="value failed">{stats.participants.certificates_failed}</span>
              </div>
            </div>
          </div>

          <div className="stats-section">
            <h3>📊 System Information</h3>
            <div className="stats-breakdown">
              <div className="breakdown-item">
                <span className="label">Database Type:</span>
                <span className="value">{stats.system?.database_type || 'PostgreSQL'}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Total Activity Logs:</span>
                <span className="value">{stats.system?.total_logs || 0}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Certificates Sent Today:</span>
                <span className="value">{stats.recent_activity?.certificates_sent_today || 0}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="admin-actions">
        <h3>🚀 Quick Actions</h3>
        
        <div className="actions-grid">
          <div className="action-section">
            <h4>📜 Certificate Management</h4>
            <div className="action-buttons">
              <button 
                onClick={handleBulkCertificateGeneration}
                disabled={actionLoading.certificates}
                className="btn-primary"
              >
                {actionLoading.certificates ? 'Processing...' : '📜 Make Certificates Available'}
              </button>
              
              <button 
                onClick={handleSendAllCertificates}
                disabled={actionLoading.sendAll}
                className="btn-success"
              >
                {actionLoading.sendAll ? 'Sending...' : '📧 Send All Pending Certificates'}
              </button>
            </div>
            <p className="action-description">
              Mark participants as attended and make certificates available for download, or send all pending certificates via email.
            </p>
          </div>

          <div className="action-section">
            <h4>📊 Data Export</h4>
            <div className="action-buttons">
              <button 
                onClick={() => exportData('csv')}
                disabled={actionLoading.export_csv}
                className="btn-secondary"
              >
                {actionLoading.export_csv ? 'Exporting...' : '📄 Export CSV'}
              </button>
              
              <button 
                onClick={() => exportData('excel')}
                disabled={actionLoading.export_excel}
                className="btn-secondary"
              >
                {actionLoading.export_excel ? 'Exporting...' : '📈 Export Excel'}
              </button>
            </div>
            <p className="action-description">
              Export participant data and session information for analysis and record-keeping.
            </p>
          </div>

          <div className="action-section">
            <h4>📈 Reports & Analytics</h4>
            <div className="action-buttons">
              <button 
                onClick={getConferenceSummary}
                disabled={loading}
                className="btn-info"
              >
                {loading ? 'Generating...' : '📊 Conference Summary'}
              </button>
              
              <button 
                onClick={() => window.open('/api/health', '_blank')}
                className="btn-outline"
              >
                🔍 System Health Check
              </button>
            </div>
            <p className="action-description">
              Generate comprehensive reports and check system status for monitoring and optimization.
            </p>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="system-status">
        <h3>🔧 System Status</h3>
        <div className="status-grid">
          <div className="status-item online">
            <span className="status-indicator">🟢</span>
            <span className="status-label">Database Connection</span>
            <span className="status-value">Online</span>
          </div>
          
          <div className="status-item online">
            <span className="status-indicator">🟢</span>
            <span className="status-label">Email Service</span>
            <span className="status-value">Active</span>
          </div>
          
          <div className="status-item online">
            <span className="status-indicator">🟢</span>
            <span className="status-label">Certificate Generation</span>
            <span className="status-value">Operational</span>
          </div>
          
          <div className="status-item online">
            <span className="status-indicator">🟢</span>
            <span className="status-label">Notification System</span>
            <span className="status-value">Active</span>
          </div>
        </div>
      </div>

      {/* Recent Activity Summary */}
      {stats.recent_activity && (
        <div className="recent-activity">
          <h3>📈 Today's Activity</h3>
          <div className="activity-summary">
            <div className="activity-item">
              <span className="activity-icon">👥</span>
              <span className="activity-text">
                {stats.recent_activity.registrations_today} new registrations
              </span>
            </div>
            
            <div className="activity-item">
              <span className="activity-icon">📧</span>
              <span className="activity-text">
                {stats.recent_activity.certificates_sent_today} certificates sent
              </span>
            </div>
            
            <div className="activity-item">
              <span className="activity-icon">📊</span>
              <span className="activity-text">
                System operating normally
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
