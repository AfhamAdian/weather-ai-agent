import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import VoiceInput from './components/VoiceInput';
import * as api from './api';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(Date.now().toString());

  const handleSend = async (text) => {
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsLoading(true);
    try {
      const { success, response, error } = await api.sendMsg(text);
      setMessages(prev => [...prev, { sender: 'bot', text: success ? response : `Error: ${error}` }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: `Error: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoice = async (file) => {
    setMessages(prev => [...prev, { sender: 'user', text: '🎤 Voice Message' }]);
    setIsLoading(true);
    try {
      const { success, response, error } = await api.sendVoice(file, sessionId);
      setMessages(prev => [...prev, { sender: 'bot', text: success ? response : `Error: ${error}` }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: `Error: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="card chat-card shadow-lg">
        <div className="card-header bg-white border-0 text-center py-3">
          <i className="bi bi-brightness-high-fill fs-2 text-warning me-2"></i>
          <span className="fs-4 fw-bold">Weather AI Assistant</span>
        </div>
        <div className="chat-window">
          <ChatWindow messages={messages} isLoading={isLoading} />
        </div>
        <div className="chat-footer d-flex align-items-center">
          <ChatInput onSend={handleSend} />
          <VoiceInput onSendVoice={handleVoice} />
        </div>
      </div>
    </div>
  );
}

export default App;

