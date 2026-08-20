import React from 'react'
import { ShieldCheck } from 'lucide-react'

export default function PIIBanner({ piiList }) {
  if (!piiList || piiList.length === 0) return null;
  
  return (
    <div style={{
      background: 'rgba(16, 185, 129, 0.1)',
      border: '1px solid rgba(16, 185, 129, 0.3)',
      borderRadius: '8px',
      padding: '8px 12px',
      margin: '8px 0',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '0.85rem',
      color: '#10b981'
    }}>
      <ShieldCheck size={16} />
      <span>
        <strong>DPDP Shield Active:</strong> Auto-redacted {piiList.join(", ")} prior to AI processing.
      </span>
    </div>
  )
}
