import React, { useState } from 'react';
import ChatMessage from './ChatMessage';
import axios from 'axios';
import { sendTextToSpeech } from '../api'; // Adjust the import path as necessary

export default function ChatWindow({ messages, isLoading }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const lastBotMsg = [...messages].reverse().find(m => m.sender === 'bot');

  const handleSpeak = async () => {
    if (!lastBotMsg) return;
    try {
      setIsSpeaking(true);
      console.log('Sending TTS request for:', lastBotMsg.text);

      const res = await sendTextToSpeech(lastBotMsg.text);
      console.log('Received TTS response:', res);

      if (!res) {
        console.error('No response from TTS');
        setIsSpeaking(false);
        return;
      }
      
      const audioUrl = URL.createObjectURL(new Blob([res]));
      const audio = new Audio(audioUrl);
      audio.play();
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsSpeaking(false);
      };
      
      audio.onerror = () => {
        console.error('Audio playback error');
        setIsSpeaking(false);
      };
    } catch (err) {
      console.error('TTS error:', err);
      setIsSpeaking(false);
    }
  };

  return (
    <div className="d-flex flex-column position-relative">
      {messages.map((msg, idx) => (
        <ChatMessage key={idx} sender={msg.sender} text={msg.text} />
      ))}

      {isLoading && (
        <div className="typing-indicator mt-2">
          <div className="spinner-border spinner-border-sm text-secondary" role="status"></div>
          <span>Weather AI is typing...</span>
        </div>
      )}

      {/* Speak Button */}
      {lastBotMsg && (
        <div className="d-flex justify-content-start mt-2">
          <button
            className="btn btn-sm rounded-pill px-3 py-1"
            style={{
              backgroundColor: '#557ade',
              color: '#fff',
              fontSize: '0.8rem',
              maxWidth: 'fit-content',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.15)'
            }}
            disabled={isSpeaking}
            onClick={handleSpeak}
          >
            <i className="bi bi-volume-up me-1"></i>
            {isSpeaking ? 'Playing...' : 'Speak'}
          </button>
        </div>
      )}
    </div>
  );
}


