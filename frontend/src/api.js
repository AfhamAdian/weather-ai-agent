import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000'
});

export const sendMsg = async (query) => {
  try {
    const res = await api.post('/sendmsg', { query });
    return res.data;
  } catch (err) {
    console.error('Error sending message:', err);
    return { success: false, error: err.message };
  }
};

export const sendVoice = async (file, sessionId) => {
  const form = new FormData();
  form.append('file', file);
  if (sessionId) form.append('session_id', sessionId);
  try {
    const res = await api.post('/sendvoice', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  } catch (err) {
    console.error('Error sending voice:', err);
    return { success: false, error: err.message };
  }
};
