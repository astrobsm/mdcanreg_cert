import React, { useState } from 'react';
import axios from 'axios';

const ConferenceRegistration = ({ onRegistrationSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    organization: '',
    position: '',
    registration_type: 'participant',
    dietary_requirements: '',
    special_needs: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    email_notifications: true,
    sms_notifications: false,
    push_notifications: true
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [step, setStep] = useState(1);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleNextStep = () => {
    // Validate required fields for current step
    if (step === 1) {
      if (!formData.name || !formData.email || !formData.phone_number) {
        setMessage('Please fill in all required fields');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        setMessage('Please enter a valid email address');
        return;
      }
    }
    setMessage('');
    setStep(step + 1);
  };

  const handlePrevStep = () => {
    setStep(step - 1);
    setMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setMessage('');
      
      const response = await axios.post('/api/register', formData);
      
      setMessage('Registration successful! Welcome to MDCAN BDM 2025.');
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        phone_number: '',
        organization: '',
        position: '',
        registration_type: 'participant',
        dietary_requirements: '',
        special_needs: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        email_notifications: true,
        sms_notifications: false,
        push_notifications: true
      });
      
      setStep(1);
      
      // Call success callback
      if (onRegistrationSuccess) {
        onRegistrationSuccess(response.data.participant);
      }
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed. Please try again.';
      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <div className="registration-header">
        <h2>🎯 Conference Registration</h2>
        <p>Join us for MDCAN BDM 14th - 2025 in Enugu</p>
        <div className="step-indicator">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>1</div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>2</div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>3</div>
        </div>
      </div>

      {message && (
        <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="registration-form">
        
        {/* Step 1: Basic Information */}
        {step === 1 && (
          <div className="form-step">
            <h3>📝 Basic Information</h3>
            
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="Enter your email address"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone_number">Phone Number *</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                required
                placeholder="Enter your phone number"
              />
            </div>

            <div className="form-group">
              <label htmlFor="registration_type">Registration Type</label>
              <select
                id="registration_type"
                name="registration_type"
                value={formData.registration_type}
                onChange={handleInputChange}
              >
                <option value="participant">Conference Participant</option>
                <option value="speaker">Speaker</option>
                <option value="organizer">Organizer</option>
                <option value="sponsor">Sponsor</option>
                <option value="volunteer">Volunteer</option>
              </select>
            </div>

            <div className="step-buttons">
              <button type="button" onClick={handleNextStep} className="btn-primary">
                Next Step →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Professional Information */}
        {step === 2 && (
          <div className="form-step">
            <h3>💼 Professional Information</h3>
            
            <div className="form-group">
              <label htmlFor="organization">Organization/Institution</label>
              <input
                type="text"
                id="organization"
                name="organization"
                value={formData.organization}
                onChange={handleInputChange}
                placeholder="Your organization or institution"
              />
            </div>

            <div className="form-group">
              <label htmlFor="position">Position/Title</label>
              <input
                type="text"
                id="position"
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                placeholder="Your job title or position"
              />
            </div>

            <div className="form-group">
              <label htmlFor="dietary_requirements">Dietary Requirements</label>
              <textarea
                id="dietary_requirements"
                name="dietary_requirements"
                value={formData.dietary_requirements}
                onChange={handleInputChange}
                rows="3"
                placeholder="Any special dietary requirements or allergies"
              />
            </div>

            <div className="form-group">
              <label htmlFor="special_needs">Special Needs/Accessibility</label>
              <textarea
                id="special_needs"
                name="special_needs"
                value={formData.special_needs}
                onChange={handleInputChange}
                rows="3"
                placeholder="Any accessibility requirements or special needs"
              />
            </div>

            <div className="step-buttons">
              <button type="button" onClick={handlePrevStep} className="btn-secondary">
                ← Previous
              </button>
              <button type="button" onClick={handleNextStep} className="btn-primary">
                Next Step →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Emergency Contact & Preferences */}
        {step === 3 && (
          <div className="form-step">
            <h3>🚨 Emergency Contact & Preferences</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="emergency_contact_name">Emergency Contact Name</label>
                <input
                  type="text"
                  id="emergency_contact_name"
                  name="emergency_contact_name"
                  value={formData.emergency_contact_name}
                  onChange={handleInputChange}
                  placeholder="Emergency contact person"
                />
              </div>

              <div className="form-group">
                <label htmlFor="emergency_contact_phone">Emergency Contact Phone</label>
                <input
                  type="tel"
                  id="emergency_contact_phone"
                  name="emergency_contact_phone"
                  value={formData.emergency_contact_phone}
                  onChange={handleInputChange}
                  placeholder="Emergency contact phone number"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Notification Preferences</label>
              <div className="checkbox-group">
                <div className="checkbox-item">
                  <input
                    type="checkbox"
                    id="email_notifications"
                    name="email_notifications"
                    checked={formData.email_notifications}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="email_notifications">📧 Email Notifications</label>
                </div>
                
                <div className="checkbox-item">
                  <input
                    type="checkbox"
                    id="sms_notifications"
                    name="sms_notifications"
                    checked={formData.sms_notifications}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="sms_notifications">📱 SMS Notifications</label>
                </div>
                
                <div className="checkbox-item">
                  <input
                    type="checkbox"
                    id="push_notifications"
                    name="push_notifications"
                    checked={formData.push_notifications}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="push_notifications">🔔 Push Notifications</label>
                </div>
              </div>
            </div>

            <div className="registration-summary">
              <h4>📋 Registration Summary</h4>
              <div className="summary-details">
                <p><strong>Name:</strong> {formData.name}</p>
                <p><strong>Email:</strong> {formData.email}</p>
                <p><strong>Type:</strong> {formData.registration_type}</p>
                {formData.organization && <p><strong>Organization:</strong> {formData.organization}</p>}
              </div>
            </div>

            <div className="step-buttons">
              <button type="button" onClick={handlePrevStep} className="btn-secondary">
                ← Previous
              </button>
              <button 
                type="submit" 
                disabled={loading} 
                className="btn-success"
              >
                {loading ? 'Registering...' : '🎯 Complete Registration'}
              </button>
            </div>
          </div>
        )}
      </form>

      <div className="registration-info">
        <h4>📅 Conference Information</h4>
        <div className="info-grid">
          <div className="info-item">
            <h5>📍 Venue</h5>
            <p>Enugu, Nigeria</p>
          </div>
          <div className="info-item">
            <h5>📅 Dates</h5>
            <p>September 1-6, 2025</p>
          </div>
          <div className="info-item">
            <h5>🎯 Focus</h5>
            <p>Professional Development</p>
          </div>
          <div className="info-item">
            <h5>🏆 Benefits</h5>
            <p>Certificate & Networking</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConferenceRegistration;
