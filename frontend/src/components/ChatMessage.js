import React from 'react';

export default function ChatMessage({ sender, text }) {
  const alignment = sender === 'user' ? 'justify-content-end' : 'justify-content-start';
  const bubbleClass = sender === 'user' ? 'user-bubble' : 'bot-bubble';

  return (
    <div className={`d-flex ${alignment} mb-3`}> 
      <div className={`bubble ${bubbleClass}`}>{text}</div>
    </div>
  );
}
