import React, { useState } from 'react';
import axios from 'axios';

const BulkUpload = ({ onParticipantsUpdated }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [sendingCertificates, setSendingCertificates] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select an Excel file first');
      return;
    }

    setUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);
      
      // Notify parent component to refresh participant list
      if (onParticipantsUpdated) {
        onParticipantsUpdated();
      }
      
      // Clear file input
      setFile(null);
      document.getElementById('excel-file-input').value = '';
      
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadResult({
        error: error.response?.data?.error || 'Upload failed'
      });
    }

    setUploading(false);
  };

  const handleBulkSend = async () => {
    if (!window.confirm('Are you sure you want to send certificates to all participants with pending status?')) {
      return;
    }

    setSendingCertificates(true);

    try {
      const response = await axios.post('/api/bulk-send-certificates');
      
      alert(`${response.data.message}\nSent: ${response.data.sent_count}\nFailed: ${response.data.failed_count}`);
      
      // Notify parent component to refresh participant list
      if (onParticipantsUpdated) {
        onParticipantsUpdated();
      }
      
    } catch (error) {
      console.error('Bulk send failed:', error);
      alert(error.response?.data?.error || 'Bulk send failed');
    }

    setSendingCertificates(false);
  };

  return (
    <div className="bulk-upload-container">
      <div className="upload-section">
        <h3>📊 Bulk Upload Participants</h3>
        <div className="file-upload-area">
          <div className="upload-instructions">
            <p><strong>Excel file requirements:</strong></p>
            <ul>
              <li><strong>Required columns:</strong> name, email</li>
              <li><strong>Optional columns:</strong> organization, position, role</li>
              <li><strong>Role values:</strong> Use "volunteer", "organizer", "staff", or "committee" for Acknowledgement of Service certificates</li>
              <li><strong>File format:</strong> .xlsx or .xls</li>
            </ul>
          </div>
          
          <div className="file-input-section">
            <input
              id="excel-file-input"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              className="file-input"
            />
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className={`upload-btn ${!file || uploading ? 'disabled' : ''}`}
            >
              {uploading ? '⏳ Uploading...' : '📤 Upload Excel File'}
            </button>
          </div>

          {file && (
            <div className="selected-file">
              <span className="file-icon">📎</span>
              <span className="file-name">{file.name}</span>
              <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        {uploadResult && (
          <div className={`upload-result ${uploadResult.error ? 'error' : 'success'}`}>
            {uploadResult.error ? (
              <div>
                <h4>❌ Upload Failed</h4>
                <p>{uploadResult.error}</p>
              </div>
            ) : (
              <div>
                <h4>✅ Upload Successful</h4>
                <p>{uploadResult.message}</p>
                <div className="result-stats">
                  <span className="stat success">✓ Added: {uploadResult.added_count}</span>
                  {uploadResult.failed_count > 0 && (
                    <span className="stat error">✗ Failed: {uploadResult.failed_count}</span>
                  )}
                </div>
                
                {uploadResult.failed_records && uploadResult.failed_records.length > 0 && (
                  <div className="failed-records">
                    <h5>Failed Records:</h5>
                    <ul>
                      {uploadResult.failed_records.map((record, index) => (
                        <li key={index}>Row {record.row}: {record.error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bulk-send-section">
        <h3>📧 Bulk Send Certificates</h3>
        <p>Send certificates to all participants with pending status.</p>
        <button
          onClick={handleBulkSend}
          disabled={sendingCertificates}
          className={`bulk-send-btn ${sendingCertificates ? 'disabled' : ''}`}
        >
          {sendingCertificates ? '⏳ Sending Certificates...' : '📧 Send All Certificates'}
        </button>
      </div>
    </div>
  );
};

export default BulkUpload;
