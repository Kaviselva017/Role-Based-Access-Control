import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/DocumentUpload.css';

const API_BASE = process.env.REACT_APP_API_URL || '';

const DocumentUpload = () => {
  const { token } = useContext(AuthContext);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [department, setDepartment] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('');

  const departments = [
    'All Roles',
    'C-level', 
    'Finance', 
    'HR', 
    'Marketing', 
    'Engineering', 
    'Sales', 
    'Operations', 
    'IT', 
    'Legal',
    'Customer Success'
  ];

  const handleFileSelect = (e) => {
    const newFiles = Array.from(e.target.files);
    checkAndAddFiles(newFiles);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const newFiles = Array.from(e.dataTransfer.files);
    checkAndAddFiles(newFiles);
  };

  const checkAndAddFiles = (newFiles) => {
    if (!newFiles || newFiles.length === 0) return;
    
    // Calculate new total size
    const currentSize = selectedFiles.reduce((acc, file) => acc + file.size, 0);
    const incomingSize = newFiles.reduce((acc, file) => acc + file.size, 0);
    
    if (currentSize + incomingSize > 16 * 1024 * 1024) {
      setMessage('Total file size cannot exceed 16MB limit');
      setMessageType('error');
      return;
    }

    setSelectedFiles(prev => [...prev, ...newFiles]);
    setMessage(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (selectedFiles.length === 0 || !department) {
      setMessage('Please select at least one file and a department');
      setMessageType('error');
      return;
    }

    setUploading(true);
    let successCount = 0;
    let errors = [];

    // Loop through each file and upload to the single-file backend endpoint
    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('department', department);

      try {
        const response = await fetch(`${API_BASE}/api/documents/upload`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        });

        if (response.ok) {
          successCount++;
        } else {
          const error = await response.json().catch(() => ({ message: 'Server error' }));
          errors.push(`${file.name}: ${error.message}`);
        }
      } catch (err) {
        errors.push(`${file.name}: ${err.message}`);
      }
      
      // Add a small 2.5-second breathing room delay between files so the AI embedding model 
      // on the backend has time to cool down and doesn't overload memory
      await new Promise(resolve => setTimeout(resolve, 2500));
    }

    setUploading(false);

    if (errors.length > 0) {
      if (successCount > 0) {
        setMessage(`Uploaded ${successCount} files, but had errors: ${errors.join(', ')}`);
        setMessageType('warning');
        setSelectedFiles([]);
      } else {
        setMessage(`Upload failed: ${errors.join(', ')}`);
        setMessageType('error');
      }
    } else {
      setMessage(`Successfully uploaded ${successCount} document(s)!`);
      setMessageType('success');
      setSelectedFiles([]); 
      // Do NOT reset department here so the user can keep uploading to the same role without re-selecting
    }
  };

  return (
    <div className="document-upload-container">
      <div className="upload-header">
        <h1>DOCUMENT UPLOAD</h1>
        <div className="header-status">
          <span className="status-dot online"></span>
          <span>SYSTEM ONLINE</span>
        </div>
      </div>

      {message && (
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleUpload} className="upload-form">
        <div
          className="drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drop-icon">📁</div>
          <p className="drop-text">Click to upload or drag & drop</p>
          <p className="drop-subtitle">TXT, MD, CSV – max 16MB</p>
          <input
            type="file"
            multiple
            onChange={handleFileSelect}
            className="file-input"
            accept=".txt,.md,.csv,.pdf"
          />
        </div>

        {selectedFiles.length > 0 && (
          <div className="file-info" style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {selectedFiles.map((file, idx) => (
              <p key={idx} className="selected-file" style={{ marginBottom: '6px' }}>
                <span>📄</span> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            ))}
          </div>
        )}

        <div className="department-section">
          <label htmlFor="department">{"// DEPARTMENT"}</label>
          <select
            id="department"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="department-select"
          >
            <option value="">Select a department...</option>
            {departments.map((dept) => (
              <option key={dept} value={dept === 'All Roles' ? 'General' : dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="upload-btn"
          disabled={uploading || selectedFiles.length === 0}
        >
          {uploading ? '⏳ UPLOADING...' : '✓ UPLOAD DOCUMENT'}
        </button>
      </form>
    </div>
  );
};

export default DocumentUpload;
