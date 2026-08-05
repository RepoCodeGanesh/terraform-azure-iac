import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import { Bot, User } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://apim-ht-ss-p-cin-01.azure-api.net/ai-assistant';

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to DevOnboard AI! I can help you understand the Azure AI Landing Zone repository, Terraform modules, and environment setup. How can I help you onboard today?',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error(`API error (${response.status})`);
      }

      const data = await response.json();
      const botMsg = {
        role: 'assistant',
        content: data.reply || data.message || 'Response received from DevOnboard assistant.',
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Could not reach DevOnboard AI Backend: ${err.message}. Please check APIM CORS configuration or endpoint availability.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-title">
          <Bot size={24} color="#3b82f6" />
          <span>DevOnboard AI Assistant</span>
          <span className="badge">CAF Platform</span>
        </div>
        <div className="user-profile">
          <User size={18} />
          <span>Entra ID Authenticated</span>
        </div>
      </header>

      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
