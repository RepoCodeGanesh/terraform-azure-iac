/**
 * BankCompliance AI — Centralized API Client Service
 * ===================================================
 * Resolves base API URL dynamically based on environment / APIM gateway:
 *   - Local dev: http://localhost:8000/api/v1
 *   - Production: https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1
 * Handles backward-compatibility with VITE_API_URL and provides unified apiFetch.
 */

export const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/compliance\/query\/?$/, '').replace(/\/$/, '')
  }
  const isLocal = typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'
  )
  return isLocal
    ? 'http://localhost:8000/api/v1'
    : 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1'
}

export const API_BASE_URL = getApiBaseUrl()

export const apiFetch = async (endpoint, options = {}) => {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  const url = `${API_BASE_URL}${cleanEndpoint}`
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  }
  
  const response = await fetch(url, {
    ...options,
    headers
  })
  
  return response
}

export default {
  baseUrl: API_BASE_URL,
  fetch: apiFetch
}
