import React from 'react';
import ChatMessage from './ChatMessage';

export default function ChatWindow({ messages, isLoading }) {
  return (
    <div className="d-flex flex-column">
      {messages.map((msg, idx) => (
        <ChatMessage key={idx} sender={msg.sender} text={msg.text} />
      ))}
      {isLoading && (
        <div className="typing-indicator mt-2"> 
          <div className="spinner-border spinner-border-sm text-secondary" role="status"></div>
          <span>Weather AI is typing...</span>
        </div>
      )}
    </div>
  );
}