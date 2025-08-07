import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MaterialsUpload.css';

const MaterialsUpload = () => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    materialType: 'brochure',
    file: null,
    isPublished: true
  });

  useEffect(() => {
    loadMaterials();
  }, []);

  const loadMaterials = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/materials');
      setMaterials(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load materials. Please try again.');
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'file') {
      setFormData({
        ...formData,
        file: files[0]
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
    if (!formData.title || !formData.materialType || !formData.file) {
      setError('Please fill all required fields and select a file');
      setLoading(false);
      return;
    }

    // Create form data for file upload
    const uploadData = new FormData();
    uploadData.append('title', formData.title);
    uploadData.append('description', formData.description || '');
    uploadData.append('material_type', formData.materialType);
    uploadData.append('file', formData.file);
    uploadData.append('is_published', formData.isPublished);

    try {
      await axios.post('/api/materials', uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        materialType: 'brochure',
        file: null,
        isPublished: true
      });
      
      // Show success message
      setSuccess('Material uploaded successfully!');
      
      // Reload materials list
      loadMaterials();
      
      // Clear file input
      document.getElementById('fileInput').value = '';
      
    } catch (err) {
      setError('Failed to upload material. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this material?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/materials/${id}`);
        setSuccess('Material deleted successfully!');
        loadMaterials();
      } catch (err) {
        setError('Failed to delete material. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const getMaterialTypeLabel = (type) => {
    const types = {
      'brochure': 'Conference Brochure',
      'video': 'Video Clip',
      'image': 'Image',
      'presentation': 'Presentation',
      'document': 'Document',
      'other': 'Other Material'
    };
    return types[type] || type;
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'brochure':
      case 'document':
        return '📄';
      case 'video':
        return '🎬';
      case 'image':
        return '🖼️';
      case 'presentation':
        return '📊';
      default:
        return '📁';
    }
  };

  return (
    <div className="materials-container">
      <h2>Conference Materials Management</h2>
      <p>Upload brochures, videos, images and other materials for the conference</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="materials-form-container">
        <h3>Upload New Material</h3>
        <form onSubmit={handleSubmit} className="materials-form">
          <div className="form-group">
            <label htmlFor="title">Title*:</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
              placeholder="Enter material title"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows="3"
              placeholder="Enter material description"
            ></textarea>
          </div>
          
          <div className="form-group">
            <label htmlFor="materialType">Material Type*:</label>
            <select
              id="materialType"
              name="materialType"
              value={formData.materialType}
              onChange={handleInputChange}
              required
            >
              <option value="brochure">Conference Brochure</option>
              <option value="video">Video Clip</option>
              <option value="image">Image</option>
              <option value="presentation">Presentation</option>
              <option value="document">Document</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="fileInput">File*:</label>
            <input
              type="file"
              id="fileInput"
              name="file"
              onChange={handleInputChange}
              required
            />
            <small>Max file size: 50MB</small>
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
            {loading ? 'Uploading...' : 'Upload Material'}
          </button>
        </form>
      </div>
      
      <div className="materials-list-container">
        <h3>Uploaded Materials</h3>
        {loading && <p>Loading materials...</p>}
        
        {materials.length === 0 && !loading ? (
          <p className="no-items">No materials uploaded yet.</p>
        ) : (
          <div className="materials-grid">
            {materials.map((material) => (
              <div key={material.id} className="material-card">
                <div className="material-icon">{getFileIcon(material.material_type)}</div>
                <div className="material-details">
                  <h4>{material.title}</h4>
                  <p className="material-type">{getMaterialTypeLabel(material.material_type)}</p>
                  {material.description && <p className="material-description">{material.description}</p>}
                  <div className="material-meta">
                    <span>Downloads: {material.download_count}</span>
                    <span>Size: {Math.round(material.file_size / 1024)} KB</span>
                  </div>
                  <div className="material-actions">
                    <a 
                      href={material.download_url}
                      className="btn-secondary"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Download
                    </a>
                    <button 
                      className="btn-danger"
                      onClick={() => handleDelete(material.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="material-status">
                  {material.is_published ? (
                    <span className="status-badge published">Published</span>
                  ) : (
                    <span className="status-badge unpublished">Unpublished</span>
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

export default MaterialsUpload;
