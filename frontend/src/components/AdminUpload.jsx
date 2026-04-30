"use client";

import { useState } from 'react';

export default function AdminUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus({ type: '', message: '' });
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus({ type: 'error', message: 'Please select a file first.' });
      return;
    }

    setLoading(true);
    setStatus({ type: '', message: '' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload-doc', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const data = await response.json();
      setStatus({ type: 'success', message: data.message });
      setFile(null); // Reset
      
      // Reset input element
      const fileInput = document.getElementById('doc-upload');
      if (fileInput) fileInput.value = '';
      
    } catch (error) {
      setStatus({ type: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <h2>HR Admin: Document Upload</h2>
      <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>
        Upload company policy documents (PDF, DOCX, TXT) to securely add them to the HR knowledge base.
      </p>

      <div className="file-input-wrapper">
        <input 
          type="file" 
          id="doc-upload" 
          accept=".pdf,.doc,.docx,.txt" 
          onChange={handleFileChange} 
        />
        <span style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
          {file ? `Selected: ${file.name}` : 'Drag & drop or click to select a document'}
        </span>
      </div>

      <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
        <button onClick={handleUpload} disabled={!file || loading}>
          {loading ? 'Uploading & Processing...' : 'Upload Document'}
        </button>
      </div>

      {status.message && (
        <div className={`status-msg status-${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  );
}
