import React, { useState } from 'react';

const ParticipantForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    position: '',
    certificateType: 'participation'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.email.trim()) {
      alert('Please fill in at least the name and email fields.');
      return;
    }
    onSubmit(formData);
    setFormData({
      name: '',
      email: '',
      organization: '',
      position: '',
      certificateType: 'participation'
    });
  };

  return (
    <div>
      <h2>Add New Participant</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Full Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="Enter participant's full name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Email Address *</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="Enter participant's email"
          />
        </div>

        <div className="form-group">
          <label htmlFor="organization">Organization</label>
          <input
            type="text"
            id="organization"
            name="organization"
            value={formData.organization}
            onChange={handleChange}
            placeholder="Enter participant's organization (optional)"
          />
        </div>

        <div className="form-group">
          <label htmlFor="position">Position/Title</label>
          <input
            type="text"
            id="position"
            name="position"
            value={formData.position}
            onChange={handleChange}
            placeholder="Enter participant's position (optional)"
          />
        </div>

        <div className="form-group">
          <label htmlFor="certificateType">Certificate Type *</label>
          <select
            id="certificateType"
            name="certificateType"
            value={formData.certificateType}
            onChange={handleChange}
            required
          >
            <option value="participation">Certificate of Participation</option>
            <option value="service">Acknowledgement of Service</option>
          </select>
        </div>

        <button type="submit" className="btn btn-success" disabled={loading}>
          {loading ? 'Adding...' : 'Add Participant'}
        </button>
      </form>
    </div>
  );
};

export default ParticipantForm;
