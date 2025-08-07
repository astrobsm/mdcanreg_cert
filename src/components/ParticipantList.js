import React from 'react';

const ParticipantList = ({ participants, onSendCertificate, onSendAllCertificates, loading }) => {
  const getStatusBadge = (status) => {
    const statusClass = status === 'sent' ? 'status-sent' : 
                       status === 'failed' ? 'status-failed' : 'status-pending';
    return (
      <span className={`status-badge ${statusClass}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Participants List ({participants.length})</h2>
        {participants.length > 0 && (
          <button
            className="btn btn-success"
            onClick={onSendAllCertificates}
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Send All Certificates'}
          </button>
        )}
      </div>

      {participants.length === 0 ? (
        <p>No participants added yet. Use the "Add Participant" tab to add participants.</p>
      ) : (
        <table className="participants-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Organization</th>
              <th>Position</th>
              <th>Certificate Type</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {participants.map((participant) => (
              <tr key={participant.id}>
                <td>{participant.name}</td>
                <td>{participant.email}</td>
                <td>{participant.organization || '-'}</td>
                <td>{participant.position || '-'}</td>
                <td>
                  <span className={`status-badge ${participant.certificate_type === 'service' ? 'status-service' : 'status-participation'}`}>
                    {participant.certificate_type === 'service' ? 'Service' : 'Participation'}
                  </span>
                </td>
                <td>{getStatusBadge(participant.certificate_status || 'pending')}</td>
                <td>
                  <button
                    className="btn"
                    onClick={() => onSendCertificate(participant.id)}
                    disabled={loading || participant.certificate_status === 'sent'}
                  >
                    {participant.certificate_status === 'sent' ? 'Sent' : 'Send Certificate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ParticipantList;
