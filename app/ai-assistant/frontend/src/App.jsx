import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import { Bot, User, Wifi, WifiOff, AlertTriangle, CheckCircle } from 'lucide-react';

// ─── URL resolution strategy ──────────────────────────────────────────────────
// Priority 1: VITE_API_URL set at build time (direct Function App URL — no APIM needed)
// Priority 2: SWA proxy route /api/* (avoids CORS entirely when both apps share origin)
// Priority 3: APIM gateway URL (requires APIM API + CORS policy in Terraform)
const API_DIRECT   = import.meta.env.VITE_API_URL;        // e.g. https://func-ht-dvob-p-cin-01.azurewebsites.net/api
const API_PROXY    = '/api';                               // SWA proxy → Function App (no CORS needed)
const API_APIM     = 'https://apim-ht-ss-p-cin-01.azure-api.net/dvob-ai-assistant';

// Use VITE_API_URL if explicitly set, otherwise use the SWA proxy (cleanest, no CORS)
const API_BASE_URL = API_DIRECT || API_PROXY;

// ─── Health check ─────────────────────────────────────────────────────────────
async function pingBackend(baseUrl) {
  try {
    const res = await fetch(`${baseUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    if (res.ok) {
      const data = await res.json();
      return { ok: true, model: data.model || 'unknown' };
    }
    return { ok: false, reason: `HTTP ${res.status}` };
  } catch (err) {
    return { ok: false, reason: err.message };
  }
}

// ─── Friendly error messages ──────────────────────────────────────────────────
function friendlyError(err) {
  const msg = err.message || '';
  if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
    return '🔌 Network error — backend unreachable. Check Azure Function App is running and CORS is configured.';
  }
  if (msg.includes('500')) {
    return '⚙️ Backend returned 500. Check Function App logs in Application Insights for the root cause (missing env vars or dependency failure).';
  }
  if (msg.includes('401') || msg.includes('403')) {
    return '🔒 Authentication error — the API requires a valid token or Subscription Key.';
  }
  if (msg.includes('404')) {
    return '🗺️ API route not found (404) — APIM API or Function route may not be deployed yet.';
  }
  return `⚠️ ${msg}`;
}

export default function App() {
  const [messages, setMessages]       = useState([
    {
      role: 'assistant',
      content: 'Welcome to DevOnboard AI! I can help you understand the Azure AI Landing Zone repository, Terraform modules, and environment setup. How can I help you onboard today?',
    },
  ]);
  const [isLoading, setIsLoading]     = useState(false);
  const [sessionId, setSessionId]     = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking' | 'ok' | 'error'
  const [backendModel, setBackendModel]   = useState('');
  const [statusReason, setStatusReason]   = useState('');

  // ─── Health pre-flight on mount ─────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      // Try primary URL first, then APIM as fallback
      let result = await pingBackend(API_BASE_URL);

      if (!result.ok && API_BASE_URL !== API_APIM) {
        result = await pingBackend(API_APIM);
      }

      if (result.ok) {
        setBackendStatus('ok');
        setBackendModel(result.model);
      } else {
        setBackendStatus('error');
        setStatusReason(result.reason);
      }
    })();
  }, []);

  // ─── Send message ────────────────────────────────────────────────────────────
  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    // Determine effective URL — prefer primary, but don't re-check every message
    const effectiveUrl = API_BASE_URL;

    try {
      const response = await fetch(`${effectiveUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`API error (${response.status})`);
      }

      const data = await response.json();

      // Persist session_id returned from backend for conversation continuity
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.reply || data.message || 'Response received.' },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: friendlyError(err), isError: true },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // ─── Status indicator ────────────────────────────────────────────────────────
  const StatusBanner = () => {
    if (backendStatus === 'checking') {
      return (
        <div className="status-banner checking">
          <Wifi size={14} className="status-icon spin" />
          <span>Connecting to backend…</span>
        </div>
      );
    }
    if (backendStatus === 'ok') {
      return (
        <div className="status-banner ok">
          <CheckCircle size={14} className="status-icon" />
          <span>Backend connected · model: <strong>{backendModel}</strong></span>
        </div>
      );
    }
    return (
      <div className="status-banner error">
        <AlertTriangle size={14} className="status-icon" />
        <span>Backend unreachable · {statusReason} — try <code>GET /api/diagnostics</code> for details</span>
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-title">
          <Bot size={24} color="#3b82f6" />
          <span>DevOnboard AI Assistant</span>
          <span className="badge">CAF Platform</span>
        </div>
        <div className="header-right">
          <StatusBanner />
          <div className="user-profile">
            <User size={18} />
            <span>Entra ID Authenticated</span>
          </div>
        </div>
      </header>

      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
