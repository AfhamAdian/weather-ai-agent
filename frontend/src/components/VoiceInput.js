import React, { useRef, useState, useEffect } from 'react';

export default function VoiceInput({ onSendVoice }) {
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [audioChunks, setAudioChunks] = useState([]);

  useEffect(() => {
    // Clean up media recorder on unmount
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      setAudioChunks([]);

      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          setAudioChunks(prev => [...prev, event.data]);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        // You can convert to mp3 server-side if needed
        onSendVoice(blob);
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error('Could not start recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div>
      {recording ? (
        <button
          onClick={stopRecording}
          className="btn btn-danger rounded-circle p-2"
          title="Stop Recording"
        >
          <i className="bi bi-stop-fill fs-4"></i>
        </button>
      ) : (
        <button
          onClick={startRecording}
          className="btn btn-light rounded-circle p-2"
          title="Start Recording"
        >
          <i className="bi bi-mic-fill text-primary fs-4"></i>
        </button>
      )}
    </div>
  );
}
