import React, { useRef } from 'react';

export default function VoiceInput({ onSendVoice }) {
  const fileRef = useRef();

  const handleUpload = (e) => {
    e.preventDefault();
    const file = fileRef.current.files[0];
    if (file) onSendVoice(file);
    fileRef.current.value = null;
  };

  return (
    <form onSubmit={handleUpload}>
      <label htmlFor="voice-upload" className="btn btn-light rounded-circle p-2">
        <i className="bi bi-mic-fill text-primary fs-4"></i>
      </label>
      <input
        id="voice-upload"
        type="file"
        accept="audio/*"
        ref={fileRef}
        className="d-none"
      />
    </form>
  );
}
