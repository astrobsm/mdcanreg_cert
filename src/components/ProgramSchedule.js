import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const ProgramSchedule = ({ currentUser, isAdmin, programs, onProgramAdded, onRefresh, onSessionRegister }) => {
  const [localPrograms, setLocalPrograms] = useState(programs || []);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProgram, setNewProgram] = useState({
    title: '',
    description: '',
    program_type: 'session',
    start_time: '',
    end_time: '',
    venue: '',
    capacity: '',
    speaker_name: '',
    speaker_bio: '',
    is_mandatory: false,
    requires_registration: false,
    reminder_minutes: 30
  });
  const [message, setMessage] = useState('');

  const loadPrograms = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedDate) params.append('date', selectedDate);
      if (selectedType) params.append('type', selectedType);
      
      const response = await axios.get(`/api/programs?${params}`);
      setLocalPrograms(response.data);
    } catch (error) {
      console.error('Error loading programs:', error);
      setMessage('Failed to load programs');
    } finally {
      setLoading(false);
    }
  }, [selectedDate, selectedType]);

  useEffect(() => {
    if (!programs) {
      loadPrograms();
    } else {
      setLocalPrograms(programs);
    }
  }, [programs, loadPrograms]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewProgram(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAddProgram = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const response = await axios.post('/api/programs', newProgram);
      
      setLocalPrograms([response.data.program, ...localPrograms]);
      setMessage('Program added successfully!');
      
      // Reset form
      setNewProgram({
        title: '',
        description: '',
        program_type: 'session',
        start_time: '',
        end_time: '',
        venue: '',
        capacity: '',
        speaker_name: '',
        speaker_bio: '',
        is_mandatory: false,
        requires_registration: false,
        reminder_minutes: 30
      });
      
      setShowAddForm(false);
      
      if (onProgramAdded) {
        onProgramAdded(response.data.program);
      }
      
      setTimeout(() => setMessage(''), 3000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to add program';
      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterForSession = async (programId) => {
    if (!currentUser) {
      setMessage('Please login to register for sessions');
      return;
    }

    try {
      setLoading(true);
      await axios.post(`/api/programs/${programId}/register`, {
        participant_id: currentUser.id
      });
      
      setMessage('Successfully registered for session!');
      
      if (onSessionRegister) {
        onSessionRegister();
      }
      
      setTimeout(() => setMessage(''), 3000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed';
      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to format date and time - used for accessibility and tooltips
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

  const formatTime = (dateTime) => {
    return new Date(dateTime).toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const groupProgramsByDate = (programs) => {
    const grouped = {};
    programs.forEach(program => {
      const date = new Date(program.start_time).toDateString();
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(program);
    });
    
    // Sort programs within each date by start time
    Object.keys(grouped).forEach(date => {
      grouped[date].sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    });
    
    return grouped;
  };

  const getProgramTypeIcon = (type) => {
    switch (type) {
      case 'keynote': return '🎤';
      case 'workshop': return '🛠️';
      case 'session': return '💼';
      case 'break': return '☕';
      case 'social': return '🥂';
      case 'networking': return '🤝';
      default: return '📋';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled': return '📅';
      case 'ongoing': return '🔴';
      case 'completed': return '✅';
      case 'cancelled': return '❌';
      default: return '📅';
    }
  };

  const groupedPrograms = groupProgramsByDate(localPrograms);

  return (
    <div className="program-schedule">
      <div className="schedule-header">
        <h2>📅 Conference Program Schedule</h2>
        <p>MDCAN BDM 14th - 2025 • Enugu • September 1-6, 2025</p>
      </div>

      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Filters */}
      <div className="schedule-filters">
        <div className="filter-group">
          <label htmlFor="date-filter">Filter by Date:</label>
          <input
            type="date"
            id="date-filter"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="type-filter">Filter by Type:</label>
          <select
            id="type-filter"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <option value="">All Types</option>
            <option value="keynote">Keynote</option>
            <option value="session">Session</option>
            <option value="workshop">Workshop</option>
            <option value="break">Break</option>
            <option value="social">Social</option>
            <option value="networking">Networking</option>
          </select>
        </div>
        
        <button onClick={loadPrograms} className="btn-secondary">
          🔍 Apply Filters
        </button>
        
        {(selectedDate || selectedType) && (
          <button 
            onClick={() => {
              setSelectedDate('');
              setSelectedType('');
              loadPrograms();
            }} 
            className="btn-outline"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Admin Controls */}
      {isAdmin && (
        <div className="admin-controls">
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-primary"
          >
            {showAddForm ? '❌ Cancel' : '➕ Add Program'}
          </button>
          
          {onRefresh && (
            <button onClick={onRefresh} className="btn-secondary">
              🔄 Refresh
            </button>
          )}
        </div>
      )}

      {/* Add Program Form */}
      {isAdmin && showAddForm && (
        <form onSubmit={handleAddProgram} className="add-program-form">
          <h3>➕ Add New Program</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Program Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={newProgram.title}
                onChange={handleInputChange}
                required
                placeholder="Enter program title"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="program_type">Type *</label>
              <select
                id="program_type"
                name="program_type"
                value={newProgram.program_type}
                onChange={handleInputChange}
                required
              >
                <option value="session">Session</option>
                <option value="keynote">Keynote</option>
                <option value="workshop">Workshop</option>
                <option value="break">Break</option>
                <option value="social">Social</option>
                <option value="networking">Networking</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={newProgram.description}
              onChange={handleInputChange}
              rows="3"
              placeholder="Program description"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start_time">Start Time *</label>
              <input
                type="datetime-local"
                id="start_time"
                name="start_time"
                value={newProgram.start_time}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="end_time">End Time *</label>
              <input
                type="datetime-local"
                id="end_time"
                name="end_time"
                value={newProgram.end_time}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="venue">Venue</label>
              <input
                type="text"
                id="venue"
                name="venue"
                value={newProgram.venue}
                onChange={handleInputChange}
                placeholder="Venue or location"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="capacity">Capacity</label>
              <input
                type="number"
                id="capacity"
                name="capacity"
                value={newProgram.capacity}
                onChange={handleInputChange}
                placeholder="Maximum participants"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="speaker_name">Speaker Name</label>
            <input
              type="text"
              id="speaker_name"
              name="speaker_name"
              value={newProgram.speaker_name}
              onChange={handleInputChange}
              placeholder="Speaker or facilitator name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="speaker_bio">Speaker Bio</label>
            <textarea
              id="speaker_bio"
              name="speaker_bio"
              value={newProgram.speaker_bio}
              onChange={handleInputChange}
              rows="3"
              placeholder="Speaker biography"
            />
          </div>

          <div className="checkbox-group">
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="is_mandatory"
                name="is_mandatory"
                checked={newProgram.is_mandatory}
                onChange={handleInputChange}
              />
              <label htmlFor="is_mandatory">Mandatory Attendance</label>
            </div>
            
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="requires_registration"
                name="requires_registration"
                checked={newProgram.requires_registration}
                onChange={handleInputChange}
              />
              <label htmlFor="requires_registration">Requires Registration</label>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={() => setShowAddForm(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Adding...' : 'Add Program'}
            </button>
          </div>
        </form>
      )}

      {/* Program Schedule */}
      {loading && <div className="loading-spinner">Loading programs...</div>}
      
      <div className="schedule-content">
        {Object.keys(groupedPrograms).length === 0 ? (
          <div className="no-programs">
            <h3>📅 No programs scheduled</h3>
            <p>Check back later for the conference schedule.</p>
          </div>
        ) : (
          Object.keys(groupedPrograms)
            .sort((a, b) => new Date(a) - new Date(b))
            .map(date => (
              <div key={date} className="schedule-day">
                <h3 className="day-header">
                  {new Date(date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </h3>
                
                <div className="programs-list">
                  {groupedPrograms[date].map(program => (
                    <div key={program.id} className={`program-card ${program.status}`}>
                      <div className="program-header">
                        <div className="program-meta">
                          <span className="program-type">
                            {getProgramTypeIcon(program.program_type)} {program.program_type}
                          </span>
                          <span className="program-status">
                            {getStatusIcon(program.status)} {program.status}
                          </span>
                          {program.is_mandatory && (
                            <span className="mandatory-badge">⚠️ Mandatory</span>
                          )}
                        </div>
                        
                        <div className="program-time" title={formatDateTime(program.start_time)}>
                          {formatTime(program.start_time)} - {formatTime(program.end_time)}
                        </div>
                      </div>
                      
                      <h4 className="program-title">{program.title}</h4>
                      
                      {program.description && (
                        <p className="program-description">{program.description}</p>
                      )}
                      
                      <div className="program-details">
                        {program.venue && (
                          <div className="detail-item">
                            <strong>📍 Venue:</strong> {program.venue}
                          </div>
                        )}
                        
                        {program.speaker_name && (
                          <div className="detail-item">
                            <strong>🎤 Speaker:</strong> {program.speaker_name}
                          </div>
                        )}
                        
                        {program.capacity && (
                          <div className="detail-item">
                            <strong>👥 Capacity:</strong> {program.registration_count || 0}/{program.capacity}
                          </div>
                        )}
                      </div>
                      
                      {program.speaker_bio && (
                        <div className="speaker-bio">
                          <strong>Speaker Bio:</strong>
                          <p>{program.speaker_bio}</p>
                        </div>
                      )}
                      
                      {/* Registration Button (for participants) */}
                      {!isAdmin && currentUser && program.requires_registration && program.status === 'scheduled' && (
                        <div className="program-actions">
                          <button 
                            onClick={() => handleRegisterForSession(program.id)}
                            disabled={loading || (program.capacity && program.registration_count >= program.capacity)}
                            className="btn-primary"
                          >
                            {loading ? 'Registering...' : '📝 Register for Session'}
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
};

export default ProgramSchedule;
