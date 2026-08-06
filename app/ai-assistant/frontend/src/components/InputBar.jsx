import React, { useState } from 'react';
import { Send } from 'lucide-react';

export default function InputBar({ onSendMessage, disabled }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text);
    setText('');
  };

  return (
    <div className="input-container">
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask DevOnboard AI about repository setup, Terraform roots, or architecture..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled}
        />
        <button type="submit" className="send-button" disabled={disabled || !text.trim()}>
          <Send size={18} />
          Send
        </button>
      </form>
    </div>
  );
}
