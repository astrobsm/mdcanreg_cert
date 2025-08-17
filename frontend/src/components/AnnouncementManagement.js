import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AnnouncementManagement.css';

const AnnouncementManagement = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    priority: 'normal',
    attachment: null,
    notifyParticipants: true,
    isPublished: true
  });

  useEffect(() => {
    loadAnnouncements();
  }, []);

  const loadAnnouncements = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/announcements');
      const announcementsData = Array.isArray(response.data) ? response.data : [];
      setAnnouncements(announcementsData);
      setLoading(false);
    } catch (err) {
      setError('Failed to load announcements. Please try again.');
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'file') {
      setFormData({
        ...formData,
        attachment: files[0]
      });
    } else if (type === 'checkbox') {
      setFormData({
        ...formData,
        [name]: checked
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate form
    if (!formData.title || !formData.content) {
      setError('Please fill all required fields');
      setLoading(false);
      return;
    }

    // Create form data for file upload
    const uploadData = new FormData();
    uploadData.append('title', formData.title);
    uploadData.append('content', formData.content);
    uploadData.append('priority', formData.priority);
    if (formData.attachment) {
      uploadData.append('attachment', formData.attachment);
    }
    uploadData.append('notify_participants', formData.notifyParticipants);
    uploadData.append('is_published', formData.isPublished);

    try {
      await axios.post('/api/announcements', uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Reset form
      setFormData({
        title: '',
        content: '',
        priority: 'normal',
        attachment: null,
        notifyParticipants: true,
        isPublished: true
      });
      
      // Show success message
      setSuccess('Announcement created successfully!' + 
        (formData.notifyParticipants ? ' Push notifications have been sent.' : ''));
      
      // Reload announcements list
      loadAnnouncements();
      
      // Clear file input
      if (document.getElementById('attachmentInput')) {
        document.getElementById('attachmentInput').value = '';
      }
      
    } catch (err) {
      setError('Failed to create announcement. Please try again.');
      console.error('Announcement error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this announcement?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/announcements/${id}`);
        setSuccess('Announcement deleted successfully!');
        loadAnnouncements();
      } catch (err) {
        setError('Failed to delete announcement. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const resendNotification = async (id) => {
    try {
      setLoading(true);
      await axios.post(`/api/announcements/${id}/notify`);
      setSuccess('Push notifications resent successfully!');
      loadAnnouncements();
    } catch (err) {
      setError('Failed to resend notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'normal':
        return 'priority-normal';
      case 'low':
        return 'priority-low';
      default:
        return 'priority-normal';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="announcements-container">
      <h2>Announcement Management</h2>
      <p>Create and manage announcements with push notifications for all participants</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="announcements-form-container">
        <h3>Create New Announcement</h3>
        <form onSubmit={handleSubmit} className="announcements-form">
          <div className="form-group">
            <label htmlFor="title">Title*:</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
              placeholder="Enter announcement title"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="content">Content*:</label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleInputChange}
              rows="5"
              required
              placeholder="Enter announcement content"
            ></textarea>
          </div>
          
          <div className="form-group">
            <label htmlFor="priority">Priority:</label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
            >
              <option value="high">High</option>
              <option value="normal">Normal</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="attachmentInput">Attachment (optional):</label>
            <input
              type="file"
              id="attachmentInput"
              name="attachment"
              onChange={handleInputChange}
            />
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="notifyParticipants"
                checked={formData.notifyParticipants}
                onChange={handleInputChange}
              />
              Send push notifications to participants
            </label>
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="isPublished"
                checked={formData.isPublished}
                onChange={handleInputChange}
              />
              Publish immediately
            </label>
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Announcement'}
          </button>
        </form>
      </div>
      
      <div className="announcements-list-container">
        <h3>All Announcements</h3>
        {loading && <p>Loading announcements...</p>}
        
        {announcements.length === 0 && !loading ? (
          <p className="no-items">No announcements created yet.</p>
        ) : (
          <div className="announcements-list">
            {announcements.map((announcement) => (
              <div key={announcement.id} className="announcement-card">
                <div className="announcement-header">
                  <h4>{announcement.title}</h4>
                  <span className={`priority-badge ${getPriorityBadgeClass(announcement.priority)}`}>
                    {announcement.priority.charAt(0).toUpperCase() + announcement.priority.slice(1)}
                  </span>
                </div>
                
                <div className="announcement-content">
                  {announcement.content}
                </div>
                
                {announcement.has_attachment && (
                  <div className="announcement-attachment">
                    <a 
                      href={announcement.attachment_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      📎 View attachment
                    </a>
                  </div>
                )}
                
                <div className="announcement-meta">
                  <span>Created: {formatDate(announcement.created_at)}</span>
                  <span>Views: {announcement.view_count}</span>
                  <span>Status: {announcement.is_published ? 'Published' : 'Unpublished'}</span>
                </div>
                
                <div className="announcement-actions">
                  <button 
                    className="btn-secondary"
                    onClick={() => resendNotification(announcement.id)}
                    disabled={loading}
                  >
                    Resend Notification
                  </button>
                  <button 
                    className="btn-danger"
                    onClick={() => handleDelete(announcement.id)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnnouncementManagement;
