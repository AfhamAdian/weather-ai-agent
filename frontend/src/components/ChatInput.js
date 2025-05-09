import React, { useState } from 'react';

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('');

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text);
    setText('');
  };

  return (
    <form onSubmit={submit} className="d-flex chat-input me-3">
      <input
        type="text"
        className="form-control"
        placeholder="Ask me anything about the weather..."
        value={text}
        onChange={e => setText(e.target.value)}
      />
      <button type="submit" className="btn btn-primary ms-2 rounded-circle p-2">
        <i className="bi bi-send-fill"></i>
      </button>
    </form>
  );
}