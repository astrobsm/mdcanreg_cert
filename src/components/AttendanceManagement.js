import React, { useState } from 'react';
import axios from 'axios';

const AttendanceManagement = ({ programs, participants, onAttendanceUpdate }) => {
  const [selectedProgram, setSelectedProgram] = useState('');
  const [attendanceData, setAttendanceData] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const handleProgramChange = (e) => {
    const programId = e.target.value;
    setSelectedProgram(programId);
    
    // Reset attendance data when switching programs
    if (programId) {
      initializeAttendanceData();
    }
  };

  const initializeAttendanceData = () => {
    const initialData = {};
    participants.forEach(participant => {
      initialData[participant.id] = 'attended'; // Default to attended
    });
    setAttendanceData(initialData);
  };

  const handleAttendanceChange = (participantId, status) => {
    setAttendanceData(prev => ({
      ...prev,
      [participantId]: status
    }));
  };

  const markAllAttendance = (status) => {
    const filteredParticipants = getFilteredParticipants();
    const newData = { ...attendanceData };
    filteredParticipants.forEach(participant => {
      newData[participant.id] = status;
    });
    setAttendanceData(newData);
  };

  const submitAttendance = async () => {
    if (!selectedProgram) {
      setMessage('Please select a program first');
      return;
    }

    try {
      setLoading(true);
      
      // Prepare attendance data for API
      const attendance = Object.entries(attendanceData).map(([participantId, status]) => ({
        participant_id: parseInt(participantId),
        status: status
      }));

      await axios.post(`/api/programs/${selectedProgram}/attendance`, { attendance });
      
      setMessage(`✅ Attendance marked for ${attendance.length} participants`);
      
      if (onAttendanceUpdate) {
        onAttendanceUpdate();
      }
      
      setTimeout(() => setMessage(''), 5000);
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to mark attendance';
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const exportAttendance = () => {
    if (!selectedProgram) {
      setMessage('Please select a program first');
      return;
    }

    const selectedProgramData = programs.find(p => p.id.toString() === selectedProgram);
    const csvData = [
      ['Name', 'Email', 'Organization', 'Registration Type', 'Attendance Status'],
      ...participants.map(participant => [
        participant.name,
        participant.email,
        participant.organization || '',
        participant.registration_type,
        attendanceData[participant.id] || 'absent'
      ])
    ];

    const csvContent = csvData.map(row => row.map(field => `"${field}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `attendance_${selectedProgramData?.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    setMessage('✅ Attendance report exported successfully');
    setTimeout(() => setMessage(''), 3000);
  };

  const getFilteredParticipants = () => {
    return participants.filter(participant => {
      const matchesSearch = participant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           participant.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (participant.organization && participant.organization.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesFilter = filterStatus === 'all' || 
                           participant.registration_status === filterStatus ||
                           participant.registration_type === filterStatus;
      
      return matchesSearch && matchesFilter;
    });
  };

  const getAttendanceStats = () => {
    const filteredParticipants = getFilteredParticipants();
    const total = filteredParticipants.length;
    const attended = filteredParticipants.filter(p => attendanceData[p.id] === 'attended').length;
    const absent = filteredParticipants.filter(p => attendanceData[p.id] === 'absent').length;
    const registered = filteredParticipants.filter(p => attendanceData[p.id] === 'registered').length;
    
    return { total, attended, absent, registered };
  };

  const formatDateTime = (dateTime) => {
    return new Date(dateTime).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const filteredParticipants = getFilteredParticipants();
  const stats = getAttendanceStats();

  return (
    <div className="attendance-management">
      <div className="attendance-header">
        <h2>✅ Attendance Management</h2>
        <p>Mark attendance for conference sessions and programs</p>
      </div>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Program Selection */}
      <div className="program-selection">
        <h3>📅 Select Program/Session</h3>
        <div className="selection-controls">
          <div className="form-group">
            <label htmlFor="program-select">Choose Program:</label>
            <select
              id="program-select"
              value={selectedProgram}
              onChange={handleProgramChange}
              className="program-selector"
            >
              <option value="">-- Select a Program --</option>
              {programs.map(program => (
                <option key={program.id} value={program.id}>
                  {program.title} - {formatDateTime(program.start_time)}
                  {program.venue && ` (${program.venue})`}
                </option>
              ))}
            </select>
          </div>
          
          {selectedProgram && (
            <div className="program-info">
              {(() => {
                const program = programs.find(p => p.id.toString() === selectedProgram);
                return program ? (
                  <div className="info-card">
                    <h4>{program.title}</h4>
                    <p>📅 {formatDateTime(program.start_time)} - {new Date(program.end_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}</p>
                    {program.venue && <p>📍 {program.venue}</p>}
                    {program.speaker_name && <p>🎤 {program.speaker_name}</p>}
                    <p>📊 Type: {program.program_type}</p>
                  </div>
                ) : null;
              })()}
            </div>
          )}
        </div>
      </div>

      {selectedProgram && (
        <>
          {/* Search and Filter Controls */}
          <div className="attendance-controls">
            <div className="control-row">
              <div className="search-section">
                <input
                  type="text"
                  placeholder="🔍 Search participants..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
                
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Participants</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="registered">Registered</option>
                  <option value="participant">Participants</option>
                  <option value="speaker">Speakers</option>
                  <option value="organizer">Organizers</option>
                </select>
              </div>
              
              <div className="bulk-actions">
                <button
                  onClick={() => markAllAttendance('attended')}
                  className="btn-success"
                >
                  ✅ Mark All Present
                </button>
                
                <button
                  onClick={() => markAllAttendance('absent')}
                  className="btn-warning"
                >
                  ❌ Mark All Absent
                </button>
                
                <button
                  onClick={exportAttendance}
                  className="btn-secondary"
                >
                  📊 Export Report
                </button>
              </div>
            </div>
          </div>

          {/* Attendance Statistics */}
          <div className="attendance-stats">
            <div className="stats-grid">
              <div className="stat-item total">
                <span className="stat-number">{stats.total}</span>
                <span className="stat-label">Total Participants</span>
              </div>
              
              <div className="stat-item attended">
                <span className="stat-number">{stats.attended}</span>
                <span className="stat-label">Present</span>
              </div>
              
              <div className="stat-item absent">
                <span className="stat-number">{stats.absent}</span>
                <span className="stat-label">Absent</span>
              </div>
              
              <div className="stat-item registered">
                <span className="stat-number">{stats.registered}</span>
                <span className="stat-label">Registered Only</span>
              </div>
            </div>
          </div>

          {/* Attendance List */}
          <div className="attendance-list">
            <div className="list-header">
              <h3>👥 Participant Attendance ({filteredParticipants.length} shown)</h3>
              
              <div className="list-actions">
                <button
                  onClick={submitAttendance}
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? 'Saving...' : '💾 Save Attendance'}
                </button>
              </div>
            </div>

            {filteredParticipants.length === 0 ? (
              <div className="empty-state">
                <h4>👥 No Participants Found</h4>
                <p>No participants match your current search and filter criteria.</p>
              </div>
            ) : (
              <div className="participants-grid">
                {filteredParticipants.map(participant => (
                  <div key={participant.id} className="participant-card">
                    <div className="participant-info">
                      <div className="participant-header">
                        <h4>{participant.name}</h4>
                        <span className={`type-badge ${participant.registration_type}`}>
                          {participant.registration_type}
                        </span>
                      </div>
                      
                      <div className="participant-details">
                        <p>📧 {participant.email}</p>
                        {participant.organization && <p>🏢 {participant.organization}</p>}
                        {participant.position && <p>💼 {participant.position}</p>}
                        <p>📋 Registration: {participant.registration_status}</p>
                      </div>
                    </div>
                    
                    <div className="attendance-selector">
                      <label>Attendance Status:</label>
                      <div className="radio-group">
                        <label className="radio-option">
                          <input
                            type="radio"
                            name={`attendance-${participant.id}`}
                            value="attended"
                            checked={attendanceData[participant.id] === 'attended'}
                            onChange={() => handleAttendanceChange(participant.id, 'attended')}
                          />
                          <span className="radio-label attended">✅ Present</span>
                        </label>
                        
                        <label className="radio-option">
                          <input
                            type="radio"
                            name={`attendance-${participant.id}`}
                            value="absent"
                            checked={attendanceData[participant.id] === 'absent'}
                            onChange={() => handleAttendanceChange(participant.id, 'absent')}
                          />
                          <span className="radio-label absent">❌ Absent</span>
                        </label>
                        
                        <label className="radio-option">
                          <input
                            type="radio"
                            name={`attendance-${participant.id}`}
                            value="registered"
                            checked={attendanceData[participant.id] === 'registered'}
                            onChange={() => handleAttendanceChange(participant.id, 'registered')}
                          />
                          <span className="radio-label registered">📝 Registered</span>
                        </label>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Save Button (Fixed at bottom) */}
          {filteredParticipants.length > 0 && (
            <div className="fixed-save-bar">
              <div className="save-info">
                <span>{stats.attended} present, {stats.absent} absent, {stats.registered} registered only</span>
              </div>
              
              <button
                onClick={submitAttendance}
                disabled={loading}
                className="btn-primary btn-large"
              >
                {loading ? 'Saving Attendance...' : '💾 Save All Attendance Records'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AttendanceManagement;
