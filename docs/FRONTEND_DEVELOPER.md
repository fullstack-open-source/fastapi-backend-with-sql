# KLIKYAI V3 - Frontend Developer Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [API Overview](#api-overview)
3. [Authentication](#authentication)
4. [Avatar Generation APIs](#avatar-generation-apis)
5. [Image Generation APIs](#image-generation-apis)
6. [Video Generation APIs](#video-generation-apis)
7. [Chat APIs](#chat-apis)
8. [User Management APIs](#user-management-apis)
9. [Health Check APIs](#health-check-apis)
10. [Error Handling](#error-handling)
11. [SDK Examples](#sdk-examples)
12. [React Integration](#react-integration)
13. [Vue.js Integration](#vuejs-integration)
14. [Mobile Integration](#mobile-integration)
15. [Best Practices](#best-practices)

## Getting Started

### Base URL
```
Production: https://api.klikyai.com
Development: http://localhost:8000
```

### API Version
All endpoints are prefixed with `/api/v3` or use the current version endpoint structure.

### Content Type
All requests should use `Content-Type: application/json` and expect JSON responses.

### Authentication
Most endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Overview

### Response Format
All API responses follow a consistent format:

#### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  },
  "meta": {
    "user_id": "user_123",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_456"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error context
    },
    "type": "ExceptionType"
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

## Authentication

### Register User
```javascript
const registerUser = async (userData) => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Login User
```javascript
const loginUser = async (credentials) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  // Store token for future requests
  localStorage.setItem('auth_token', result.data.access_token);
  
  return result.data;
};
```

### Token Management
```javascript
class AuthManager {
  constructor() {
    this.token = localStorage.getItem('auth_token');
  }
  
  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }
  
  getToken() {
    return this.token;
  }
  
  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }
  
  isAuthenticated() {
    return !!this.token;
  }
  
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }
}
```

## Avatar Generation APIs

### Get Available Avatars
```javascript
const getAvatars = async () => {
  const response = await fetch('/ai/heygen/avatars', {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Usage
try {
  const avatars = await getAvatars();
  console.log(`Found ${avatars.total_avatars} avatars`);
  avatars.avatars.forEach(avatar => {
    console.log(`${avatar.avatar_name} (${avatar.gender})`);
  });
} catch (error) {
  console.error('Failed to fetch avatars:', error.message);
}
```

### Get Available Voices
```javascript
const getVoices = async () => {
  const response = await fetch('/ai/heygen/voices', {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Generate Avatar Video
```javascript
const generateAvatarVideo = async (videoData) => {
  const response = await fetch('/ai/heygen/avatar-video-generation', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      avatar_id: videoData.avatarId,
      voice_id: videoData.voiceId,
      text: videoData.text,
      dimension: videoData.dimension || '16:9',
      quality: videoData.quality || 'medium',
      caption: videoData.caption || false,
      emotion: videoData.emotion,
      background: videoData.background,
      speed: videoData.speed || 1.0
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Usage
try {
  const videoResult = await generateAvatarVideo({
    avatarId: 'Abigail_expressive_2024112501',
    voiceId: 'voice_123',
    text: 'Hello, welcome to our presentation!',
    dimension: '16:9',
    quality: 'high',
    caption: true,
    emotion: 'happy'
  });
  
  console.log('Video generated:', videoResult.video_url);
} catch (error) {
  console.error('Video generation failed:', error.message);
}
```

### Check Video Status
```javascript
const checkVideoStatus = async (videoId) => {
  const response = await fetch(`/ai/heygen/videos/${videoId}`, {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Polling example
const pollVideoStatus = async (videoId, onUpdate, maxAttempts = 30) => {
  let attempts = 0;
  
  const poll = async () => {
    try {
      const status = await checkVideoStatus(videoId);
      onUpdate(status);
      
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }
      
      if (attempts < maxAttempts) {
        attempts++;
        setTimeout(poll, 5000); // Poll every 5 seconds
      } else {
        throw new Error('Video generation timeout');
      }
    } catch (error) {
      console.error('Status check failed:', error);
      throw error;
    }
  };
  
  return poll();
};
```

## Image Generation APIs

### Generate Image
```javascript
const generateImage = async (imageData) => {
  const response = await fetch('/ai/leonardo-image-generation', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      prompt: imageData.prompt,
      model: imageData.model || 'LEONARDO',
      width: imageData.width || 832,
      height: imageData.height || 480,
      num_images: imageData.numImages || 1,
      style: imageData.style,
      negative_prompt: imageData.negativePrompt
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Usage
try {
  const imageResult = await generateImage({
    prompt: 'A beautiful sunset over mountains',
    model: 'LEONARDO',
    width: 1024,
    height: 768,
    style: 'photographic'
  });
  
  console.log('Images generated:', imageResult.images);
} catch (error) {
  console.error('Image generation failed:', error.message);
}
```

### Upscale Image
```javascript
const upscaleImage = async (imageUrl, scale = 2) => {
  const response = await fetch('/ai/upscale-image', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      image_url: imageUrl,
      scale: scale
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

## Video Generation APIs

### Generate Video from Text
```javascript
const generateVideoFromText = async (videoData) => {
  const response = await fetch('/ai/leonardo-video-generation', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      prompt: videoData.prompt,
      model: videoData.model || 'MOTION_2_0',
      width: videoData.width || 832,
      height: videoData.height || 480,
      negative_prompt: videoData.negativePrompt,
      frameInterpolation: videoData.frameInterpolation || true,
      promptEnhance: videoData.promptEnhance || true
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Generate Video from Image
```javascript
const generateVideoFromImage = async (videoData) => {
  const response = await fetch('/ai/leonardo-video-generation', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      prompt: videoData.prompt,
      init_image_url: videoData.imageUrl,
      model: videoData.model || 'MOTION_2_0',
      width: videoData.width || 832,
      height: videoData.height || 480
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

## Chat APIs

### Send Chat Message
```javascript
const sendChatMessage = async (messageData) => {
  const response = await fetch('/ai/chat/send-message', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      message: messageData.message,
      conversation_id: messageData.conversationId,
      model: messageData.model || 'gpt-4',
      temperature: messageData.temperature || 0.7,
      max_tokens: messageData.maxTokens || 1000
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Streaming example
const sendChatMessageStream = async (messageData, onChunk) => {
  const response = await fetch('/ai/chat/send-message-stream', {
    method: 'POST',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      message: messageData.message,
      conversation_id: messageData.conversationId,
      model: messageData.model || 'gpt-4'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          
          try {
            const parsed = JSON.parse(data);
            onChunk(parsed);
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
};
```

### Get Chat History
```javascript
const getChatHistory = async (conversationId, limit = 50, offset = 0) => {
  const response = await fetch(
    `/ai/chat/history/${conversationId}?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: authManager.getAuthHeaders()
    }
  );
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

## User Management APIs

### Get User Profile
```javascript
const getUserProfile = async () => {
  const response = await fetch('/auth/profile', {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Update User Profile
```javascript
const updateUserProfile = async (profileData) => {
  const response = await fetch('/auth/profile', {
    method: 'PUT',
    headers: authManager.getAuthHeaders(),
    body: JSON.stringify({
      full_name: profileData.fullName,
      username: profileData.username,
      avatar_url: profileData.avatarUrl
    })
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Get Wallet Balance
```javascript
const getWalletBalance = async () => {
  const response = await fetch('/wallets/balance', {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Get Wallet Transactions
```javascript
const getWalletTransactions = async (limit = 20, offset = 0) => {
  const response = await fetch(
    `/wallets/transactions?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: authManager.getAuthHeaders()
    }
  );
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

## Health Check APIs

### System Health Check
```javascript
const getSystemHealth = async () => {
  const response = await fetch('/health/system');
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};
```

### Services Health Check
```javascript
const getServicesHealth = async () => {
  const response = await fetch('/health/services', {
    method: 'GET',
    headers: authManager.getAuthHeaders()
  });
  
  const result = await response.json();
  
  if (!response.ok) {
    throw new Error(result.error.message);
  }
  
  return result.data;
};

// Usage
try {
  const health = await getServicesHealth();
  console.log(`Overall status: ${health.overall_status}`);
  console.log(`Healthy services: ${health.healthy_services}/${health.total_services}`);
  
  Object.entries(health.services).forEach(([service, status]) => {
    console.log(`${service}: ${status.status} (${status.response_time}ms)`);
  });
} catch (error) {
  console.error('Health check failed:', error.message);
}
```

### Specific Service Health Checks
```javascript
// HeyGen API health
const getHeyGenHealth = async () => {
  const response = await fetch('/health/heygen', {
    headers: authManager.getAuthHeaders()
  });
  return response.json();
};

// Leonardo AI health
const getLeonardoHealth = async () => {
  const response = await fetch('/health/leonardo', {
    headers: authManager.getAuthHeaders()
  });
  return response.json();
};

// Database health
const getDatabaseHealth = async () => {
  const response = await fetch('/health/database', {
    headers: authManager.getAuthHeaders()
  });
  return response.json();
};
```

## Error Handling

### Global Error Handler
```javascript
class APIError extends Error {
  constructor(message, code, details = {}) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.details = details;
  }
}

const handleAPIResponse = async (response) => {
  const result = await response.json();
  
  if (!response.ok) {
    throw new APIError(
      result.error.message,
      result.error.code,
      result.error.details
    );
  }
  
  return result.data;
};
```

### Retry Logic
```javascript
const retryRequest = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Don't retry on client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};
```

### Rate Limit Handling
```javascript
const makeRequestWithRateLimit = async (requestFn) => {
  try {
    return await requestFn();
  } catch (error) {
    if (error.status === 429) {
      const retryAfter = error.headers.get('Retry-After');
      const delay = retryAfter ? parseInt(retryAfter) * 1000 : 60000;
      
      console.log(`Rate limited. Retrying after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return await requestFn();
    }
    throw error;
  }
};
```

## SDK Examples

### JavaScript SDK
```javascript
class KLIKYAIClient {
  constructor(baseURL = 'https://api.klikyai.com', apiKey = null) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
    this.authManager = new AuthManager();
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    if (this.authManager.isAuthenticated()) {
      headers.Authorization = `Bearer ${this.authManager.getToken()}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    return handleAPIResponse(response);
  }
  
  // Authentication methods
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }
  
  async login(credentials) {
    const result = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    
    this.authManager.setToken(result.access_token);
    return result;
  }
  
  // Avatar methods
  async getAvatars() {
    return this.request('/ai/heygen/avatars');
  }
  
  async generateAvatarVideo(videoData) {
    return this.request('/ai/heygen/avatar-video-generation', {
      method: 'POST',
      body: JSON.stringify(videoData)
    });
  }
  
  // Image methods
  async generateImage(imageData) {
    return this.request('/ai/leonardo-image-generation', {
      method: 'POST',
      body: JSON.stringify(imageData)
    });
  }
  
  // Chat methods
  async sendChatMessage(messageData) {
    return this.request('/ai/chat/send-message', {
      method: 'POST',
      body: JSON.stringify(messageData)
    });
  }
  
  // Health methods
  async getHealth() {
    return this.request('/health/services');
  }
}

// Usage
const client = new KLIKYAIClient();

// Login
await client.login({
  email: 'user@example.com',
  password: 'password'
});

// Generate avatar video
const video = await client.generateAvatarVideo({
  avatarId: 'Abigail_expressive_2024112501',
  voiceId: 'voice_123',
  text: 'Hello world!'
});
```

## React Integration

### React Hook for API Calls
```javascript
import { useState, useEffect, useCallback } from 'react';

const useKLIKYAI = () => {
  const [client] = useState(() => new KLIKYAIClient());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const makeRequest = useCallback(async (requestFn) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await requestFn();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    client,
    loading,
    error,
    makeRequest
  };
};

// Avatar generation hook
const useAvatarGeneration = () => {
  const { client, loading, error, makeRequest } = useKLIKYAI();
  const [avatars, setAvatars] = useState([]);
  const [voices, setVoices] = useState([]);
  
  const loadAvatars = useCallback(async () => {
    const result = await makeRequest(() => client.getAvatars());
    setAvatars(result.avatars);
  }, [makeRequest, client]);
  
  const loadVoices = useCallback(async () => {
    const result = await makeRequest(() => client.getVoices());
    setVoices(result.voices);
  }, [makeRequest, client]);
  
  const generateVideo = useCallback(async (videoData) => {
    return makeRequest(() => client.generateAvatarVideo(videoData));
  }, [makeRequest, client]);
  
  useEffect(() => {
    loadAvatars();
    loadVoices();
  }, [loadAvatars, loadVoices]);
  
  return {
    avatars,
    voices,
    generateVideo,
    loading,
    error
  };
};
```

### React Component Example
```javascript
import React, { useState } from 'react';
import { useAvatarGeneration } from './hooks/useKLIKYAI';

const AvatarGenerator = () => {
  const { avatars, voices, generateVideo, loading, error } = useAvatarGeneration();
  const [formData, setFormData] = useState({
    avatarId: '',
    voiceId: '',
    text: '',
    quality: 'medium'
  });
  const [result, setResult] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const videoResult = await generateVideo(formData);
      setResult(videoResult);
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    return <div>Error: {error}</div>;
  }
  
  return (
    <div>
      <h2>Avatar Video Generator</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Avatar:</label>
          <select name="avatarId" value={formData.avatarId} onChange={handleChange}>
            <option value="">Select an avatar</option>
            {avatars.map(avatar => (
              <option key={avatar.avatar_id} value={avatar.avatar_id}>
                {avatar.avatar_name}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Voice:</label>
          <select name="voiceId" value={formData.voiceId} onChange={handleChange}>
            <option value="">Select a voice</option>
            {voices.map(voice => (
              <option key={voice.voice_id} value={voice.voice_id}>
                {voice.name} ({voice.language})
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Text:</label>
          <textarea
            name="text"
            value={formData.text}
            onChange={handleChange}
            placeholder="Enter text for the avatar to speak"
            rows={4}
          />
        </div>
        
        <div>
          <label>Quality:</label>
          <select name="quality" value={formData.quality} onChange={handleChange}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        
        <button type="submit" disabled={loading}>
          Generate Video
        </button>
      </form>
      
      {result && (
        <div>
          <h3>Generated Video</h3>
          <video controls src={result.video_url} />
          <p>Status: {result.status}</p>
        </div>
      )}
    </div>
  );
};

export default AvatarGenerator;
```

## Vue.js Integration

### Vue Composable
```javascript
import { ref, reactive } from 'vue';

export const useKLIKYAI = () => {
  const client = new KLIKYAIClient();
  const loading = ref(false);
  const error = ref(null);
  
  const makeRequest = async (requestFn) => {
    loading.value = true;
    error.value = null;
    
    try {
      const result = await requestFn();
      return result;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  return {
    client,
    loading,
    error,
    makeRequest
  };
};

export const useAvatarGeneration = () => {
  const { client, loading, error, makeRequest } = useKLIKYAI();
  const avatars = ref([]);
  const voices = ref([]);
  
  const loadAvatars = async () => {
    const result = await makeRequest(() => client.getAvatars());
    avatars.value = result.avatars;
  };
  
  const loadVoices = async () => {
    const result = await makeRequest(() => client.getVoices());
    voices.value = result.voices;
  };
  
  const generateVideo = async (videoData) => {
    return makeRequest(() => client.generateAvatarVideo(videoData));
  };
  
  return {
    avatars,
    voices,
    generateVideo,
    loadAvatars,
    loadVoices,
    loading,
    error
  };
};
```

### Vue Component Example
```vue
<template>
  <div>
    <h2>Avatar Video Generator</h2>
    
    <form @submit.prevent="handleSubmit">
      <div>
        <label>Avatar:</label>
        <select v-model="formData.avatarId">
          <option value="">Select an avatar</option>
          <option 
            v-for="avatar in avatars" 
            :key="avatar.avatar_id" 
            :value="avatar.avatar_id"
          >
            {{ avatar.avatar_name }}
          </option>
        </select>
      </div>
      
      <div>
        <label>Voice:</label>
        <select v-model="formData.voiceId">
          <option value="">Select a voice</option>
          <option 
            v-for="voice in voices" 
            :key="voice.voice_id" 
            :value="voice.voice_id"
          >
            {{ voice.name }} ({{ voice.language }})
          </option>
        </select>
      </div>
      
      <div>
        <label>Text:</label>
        <textarea
          v-model="formData.text"
          placeholder="Enter text for the avatar to speak"
          rows="4"
        />
      </div>
      
      <div>
        <label>Quality:</label>
        <select v-model="formData.quality">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      
      <button type="submit" :disabled="loading">
        Generate Video
      </button>
    </form>
    
    <div v-if="result">
      <h3>Generated Video</h3>
      <video controls :src="result.video_url" />
      <p>Status: {{ result.status }}</p>
    </div>
    
    <div v-if="error" class="error">
      Error: {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useAvatarGeneration } from './composables/useKLIKYAI';

const { avatars, voices, generateVideo, loadAvatars, loadVoices, loading, error } = useAvatarGeneration();

const formData = reactive({
  avatarId: '',
  voiceId: '',
  text: '',
  quality: 'medium'
});

const result = ref(null);

const handleSubmit = async () => {
  try {
    const videoResult = await generateVideo(formData);
    result.value = videoResult;
  } catch (err) {
    console.error('Generation failed:', err);
  }
};

onMounted(() => {
  loadAvatars();
  loadVoices();
});
</script>
```

## Mobile Integration

### React Native Example
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

class MobileKLIKYAIClient extends KLIKYAIClient {
  constructor(baseURL = 'https://api.klikyai.com') {
    super(baseURL);
  }
  
  async setToken(token) {
    this.authManager.setToken(token);
    await AsyncStorage.setItem('auth_token', token);
  }
  
  async getToken() {
    if (!this.authManager.getToken()) {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        this.authManager.setToken(token);
      }
    }
    return this.authManager.getToken();
  }
  
  async clearToken() {
    this.authManager.clearToken();
    await AsyncStorage.removeItem('auth_token');
  }
  
  async request(endpoint, options = {}) {
    const token = await this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    return handleAPIResponse(response);
  }
}

// React Native hook
const useMobileKLIKYAI = () => {
  const [client] = useState(() => new MobileKLIKYAIClient());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const makeRequest = useCallback(async (requestFn) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await requestFn();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    client,
    loading,
    error,
    makeRequest
  };
};
```

### Flutter/Dart Example
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class KLIKYAIClient {
  final String baseURL;
  String? _token;
  
  KLIKYAIClient({this.baseURL = 'https://api.klikyai.com'});
  
  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  Future<String?> getToken() async {
    if (_token == null) {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('auth_token');
    }
    return _token;
  }
  
  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
  
  Future<Map<String, dynamic>> request(
    String endpoint, {
    String method = 'GET',
    Map<String, dynamic>? body,
  }) async {
    final token = await getToken();
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    
    final url = Uri.parse('$baseURL$endpoint');
    http.Response response;
    
    switch (method.toUpperCase()) {
      case 'POST':
        response = await http.post(url, headers: headers, body: jsonEncode(body));
        break;
      case 'PUT':
        response = await http.put(url, headers: headers, body: jsonEncode(body));
        break;
      case 'DELETE':
        response = await http.delete(url, headers: headers);
        break;
      default:
        response = await http.get(url, headers: headers);
    }
    
    final result = jsonDecode(response.body);
    
    if (response.statusCode >= 400) {
      throw Exception(result['error']['message']);
    }
    
    return result['data'];
  }
  
  // Avatar methods
  Future<List<dynamic>> getAvatars() async {
    final result = await request('/ai/heygen/avatars');
    return result['avatars'];
  }
  
  Future<Map<String, dynamic>> generateAvatarVideo(Map<String, dynamic> videoData) async {
    return await request('/ai/heygen/avatar-video-generation',
        method: 'POST', body: videoData);
  }
  
  // Authentication methods
  Future<Map<String, dynamic>> login(String email, String password) async {
    final result = await request('/auth/login',
        method: 'POST',
        body: {'email': email, 'password': password});
    
    await setToken(result['access_token']);
    return result;
  }
}
```

## Best Practices

### 1. Error Handling
```javascript
// Always handle errors gracefully
try {
  const result = await client.generateAvatarVideo(videoData);
  // Handle success
} catch (error) {
  if (error.code === 'INSUFFICIENT_CREDITS') {
    // Show credit purchase dialog
  } else if (error.code === 'RATE_LIMITED') {
    // Show rate limit message
  } else {
    // Show generic error message
  }
}
```

### 2. Loading States
```javascript
// Always show loading states for better UX
const [loading, setLoading] = useState(false);

const handleGenerate = async () => {
  setLoading(true);
  try {
    const result = await generateVideo(data);
    // Handle result
  } finally {
    setLoading(false);
  }
};
```

### 3. Caching
```javascript
// Cache frequently accessed data
const cache = new Map();

const getCachedAvatars = async () => {
  if (cache.has('avatars')) {
    return cache.get('avatars');
  }
  
  const avatars = await client.getAvatars();
  cache.set('avatars', avatars);
  return avatars;
};
```

### 4. Retry Logic
```javascript
// Implement retry logic for network requests
const retryRequest = async (requestFn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
};
```

### 5. TypeScript Support
```typescript
// Define types for better development experience
interface Avatar {
  avatar_id: string;
  avatar_name: string;
  gender: string;
  preview_image_url: string;
  preview_video_url: string;
  premium: boolean;
}

interface VideoGenerationRequest {
  avatar_id: string;
  voice_id: string;
  text: string;
  dimension?: '16:9' | '9:16' | '1:1';
  quality?: 'low' | 'medium' | 'high';
  caption?: boolean;
  emotion?: string;
}

interface VideoGenerationResponse {
  video_id: string;
  video_url: string;
  thumbnail_url: string;
  status: string;
  duration?: number;
}

// Use typed client methods
const generateVideo = async (data: VideoGenerationRequest): Promise<VideoGenerationResponse> => {
  return client.generateAvatarVideo(data);
};
```

This frontend developer documentation provides comprehensive examples and best practices for integrating with the KLIKYAI V3 API across different platforms and frameworks.
