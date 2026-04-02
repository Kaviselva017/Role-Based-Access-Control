import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/DocumentUpload.css';

const API_BASE = process.env.REACT_APP_API_URL || '';

const DocumentUpload = () => {
  const { token } = useContext(AuthContext);
  const [selectedFile, setSelectedFile] = useState(null);
  const [department, setDepartment] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('');

  const departments = ['Finance', 'HR', 'Marketing', 'Engineering'];

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile || !department) {
      setMessage('Please select a file and department');
      setMessageType('error');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('department', department);

    try {
      const response = await fetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        await response.json();
        setMessage(`Document "${selectedFile.name}" uploaded successfully!`);
        setMessageType('success');
        setSelectedFile(null);
        setDepartment('');
      } else {
        const error = await response.json();
        setMessage(error.message);
        setMessageType('error');
      }
    } catch (err) {
      setMessage(err.message);
      setMessageType('error');
    } finally {
      setUploading(false);
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
            onChange={handleFileSelect}
            className="file-input"
            accept=".txt,.md,.csv,.pdf"
          />
        </div>

        {selectedFile && (
          <div className="file-info">
            <p className="selected-file">
              <span>📄</span> {selectedFile.name}
            </p>
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
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="upload-btn"
          disabled={uploading || !selectedFile}
        >
          {uploading ? '⏳ UPLOADING...' : '✓ UPLOAD DOCUMENT'}
        </button>
      </form>
    </div>
  );
};

export default DocumentUpload;
