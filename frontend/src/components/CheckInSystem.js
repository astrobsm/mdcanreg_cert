import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CheckInSystem.css';

const CheckInSystem = () => {
  const [participants, setParticipants] = useState([]);
  const [filteredParticipants, setFilteredParticipants] = useState([]);
  const [checkedInParticipants, setCheckedInParticipants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [conferenceDay, setConferenceDay] = useState(1);
  const [stats, setStats] = useState({
    totalParticipants: 0,
    checkedIn: 0,
    materialsProvided: 0,
    percentCheckedIn: 0
  });

  useEffect(() => {
    loadParticipants();
    loadCheckedInParticipants();
  }, [conferenceDay]);

  // Filter participants based on search term
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredParticipants(participants);
    } else {
      const filtered = participants.filter(
        (participant) =>
          participant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          participant.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (participant.certificate_number && 
            participant.certificate_number.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredParticipants(filtered);
    }
  }, [searchTerm, participants]);

  const loadParticipants = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/participants');
      setParticipants(response.data);
      setFilteredParticipants(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load participants. Please try again.');
      setLoading(false);
    }
  };

  const loadCheckedInParticipants = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/check-ins/day/${conferenceDay}`);
      setCheckedInParticipants(response.data);
      
      // Calculate stats
      if (participants.length > 0) {
        const checkedInCount = response.data.length;
        const materialsProvidedCount = response.data.filter(c => c.materials_received).length;
        const percentCheckedIn = Math.round((checkedInCount / participants.length) * 100);
        
        setStats({
          totalParticipants: participants.length,
          checkedIn: checkedInCount,
          materialsProvided: materialsProvidedCount,
          percentCheckedIn: percentCheckedIn
        });
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load check-ins:', err);
      setLoading(false);
    }
  };

  const handleCheckIn = async (participantId, hasMaterials = false) => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      await axios.post('/api/check-ins', {
        participant_id: participantId,
        check_in_day: conferenceDay,
        materials_received: hasMaterials,
        verification_method: 'manual'
      });
      
      setSuccess('Participant checked in successfully!');
      
      // Reload check-ins to update the list
      loadCheckedInParticipants();
      
      // If it's the last day, generate certificate
      if (conferenceDay === 6) {
        try {
          await axios.post(`/api/participants/${participantId}/generate-certificate`);
          setSuccess('Participant checked in and certificate generated successfully!');
        } catch (certErr) {
          console.error('Certificate generation error:', certErr);
          setSuccess('Participant checked in, but certificate generation failed.');
        }
      }
      
    } catch (err) {
      setError('Failed to check in participant. Please try again.');
      console.error('Check-in error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProvideMaterials = async (checkInId) => {
    try {
      setLoading(true);
      setError('');
      
      await axios.put(`/api/check-ins/${checkInId}`, {
        materials_received: true
      });
      
      setSuccess('Materials marked as provided successfully!');
      
      // Reload check-ins to update the list
      loadCheckedInParticipants();
      
    } catch (err) {
      setError('Failed to update materials status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isCheckedIn = (participantId) => {
    return checkedInParticipants.some(checkin => checkin.participant_id === participantId);
  };

  const getCheckInDetails = (participantId) => {
    return checkedInParticipants.find(checkin => checkin.participant_id === participantId);
  };

  const handleConferenceDayChange = (e) => {
    setConferenceDay(parseInt(e.target.value, 10));
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="checkin-container">
      <h2>Conference Check-In System</h2>
      <p>Manage participant check-ins and conference materials distribution</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="checkin-controls">
        <div className="conference-day-selector">
          <label htmlFor="conferenceDay">Conference Day:</label>
          <select 
            id="conferenceDay" 
            value={conferenceDay}
            onChange={handleConferenceDayChange}
            className="day-select"
          >
            <option value={1}>Day 1</option>
            <option value={2}>Day 2</option>
            <option value={3}>Day 3</option>
            <option value={4}>Day 4</option>
            <option value={5}>Day 5</option>
            <option value={6}>Day 6 (Final Day)</option>
          </select>
          
          {conferenceDay === 6 && (
            <span className="certificate-note">
              Final day check-ins will trigger certificate generation!
            </span>
          )}
        </div>
        
        <div className="search-container">
          <input
            type="text"
            placeholder="Search participants by name, email or certificate number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>
      
      <div className="stats-container">
        <div className="stat-card">
          <h3>Total Registered</h3>
          <p className="stat-value">{stats.totalParticipants}</p>
        </div>
        <div className="stat-card">
          <h3>Checked In Today</h3>
          <p className="stat-value">{stats.checkedIn}</p>
          <p className="stat-percent">{stats.percentCheckedIn}%</p>
        </div>
        <div className="stat-card">
          <h3>Materials Provided</h3>
          <p className="stat-value">{stats.materialsProvided}</p>
        </div>
      </div>
      
      <div className="participants-container">
        <h3>Participants List</h3>
        {loading && <p className="loading">Loading participants...</p>}
        
        {filteredParticipants.length === 0 && !loading ? (
          <p className="no-items">No participants found matching your search.</p>
        ) : (
          <table className="participants-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredParticipants.map((participant) => {
                const checkedIn = isCheckedIn(participant.id);
                const checkInDetails = checkedIn ? getCheckInDetails(participant.id) : null;
                
                return (
                  <tr key={participant.id} className={checkedIn ? 'checked-in-row' : ''}>
                    <td>{participant.name}</td>
                    <td>{participant.email}</td>
                    <td>
                      {checkedIn ? (
                        <div className="status-info">
                          <span className="checked-in-badge">
                            ✓ Checked in at {formatDate(checkInDetails.check_in_time)}
                          </span>
                          {checkInDetails.materials_received ? (
                            <span className="materials-badge">Materials provided</span>
                          ) : null}
                        </div>
                      ) : (
                        <span className="not-checked-badge">Not checked in</span>
                      )}
                    </td>
                    <td>
                      {!checkedIn ? (
                        <div className="action-buttons">
                          <button
                            onClick={() => handleCheckIn(participant.id, false)}
                            className="btn-check-in"
                            disabled={loading}
                          >
                            Check In
                          </button>
                          <button
                            onClick={() => handleCheckIn(participant.id, true)}
                            className="btn-materials"
                            disabled={loading}
                          >
                            Check In + Materials
                          </button>
                        </div>
                      ) : !checkInDetails.materials_received ? (
                        <button
                          onClick={() => handleProvideMaterials(checkInDetails.id)}
                          className="btn-provide-materials"
                          disabled={loading}
                        >
                          Provide Materials
                        </button>
                      ) : (
                        <span className="all-complete">All Complete ✓</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
      
      <div className="checkin-footer">
        <button 
          className="btn-refresh" 
          onClick={() => {
            loadParticipants();
            loadCheckedInParticipants();
          }}
          disabled={loading}
        >
          Refresh Data
        </button>
        
        {conferenceDay === 6 && (
          <button
            className="btn-generate-all-certificates"
            onClick={async () => {
              if (window.confirm('Are you sure you want to generate certificates for all checked-in participants?')) {
                try {
                  setLoading(true);
                  await axios.post('/api/certificates/generate-all');
                  setSuccess('All certificates have been generated and sent successfully!');
                } catch (err) {
                  setError('Failed to generate all certificates. Please try again.');
                } finally {
                  setLoading(false);
                }
              }
            }}
            disabled={loading}
          >
            Generate All Certificates
          </button>
        )}
      </div>
    </div>
  );
};

export default CheckInSystem;
