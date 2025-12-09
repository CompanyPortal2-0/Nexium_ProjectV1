# File Management API Documentation

**Version:** 1.0  
**Base URL:** `https://localhost:7050`  
**Authentication:** JWT Bearer Token (required for all endpoints)

## Overview

This API provides file management capabilities including uploading, listing, and downloading files. All endpoints require JWT authentication via the `Authorization` header.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Upload File](#1-upload-file)
   - [List All Files](#2-list-all-files)
   - [Download File](#3-download-file)
3. [Error Handling](#error-handling)
4. [Examples](#examples)
   - [JavaScript/Fetch Examples](#javascript-fetch-examples)
   - [cURL Examples](#curl-examples)
   - [Python Examples](#python-examples)

---

## Authentication

All file endpoints require a valid JWT token obtained from the `/login` endpoint.

### Getting a Token

```http
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Using the Token

Include the token in the `Authorization` header for all file requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Endpoints

### 1. Upload File

Upload a file to the server.

**Endpoint:** `POST /files/upload`

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data` (automatic when using FormData)

**Request Body:**
- `file`: The file to upload (multipart/form-data)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "document.pdf",
  "user_email": "user@example.com"
}
```

**Error Responses:**

- **400 Bad Request** - No file provided or empty filename
```json
{
  "success": false,
  "error": "No file provided"
}
```

- **401 Unauthorized** - Invalid or missing JWT token
```json
{
  "msg": "Missing Authorization Header"
}
```

- **503 Service Unavailable** - Data service is down
```json
{
  "success": false,
  "error": "Service communication error: Connection refused"
}
```

---

### 2. List All Files

Get a list of all uploaded files.

**Endpoint:** `GET /files`

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:** None

**Success Response (200 OK):**
```json
{
  "success": true,
  "files": [
    "document.pdf",
    "image.png",
    "report.xlsx",
    "presentation.pptx"
  ],
  "count": 4
}
```

**Error Responses:**

- **401 Unauthorized** - Invalid or missing JWT token
```json
{
  "msg": "Missing Authorization Header"
}
```

- **503 Service Unavailable** - Data service is down
```json
{
  "success": false,
  "error": "Service communication error: Connection refused"
}
```

---

### 3. Download File

Download a specific file by its filename.

**Endpoint:** `GET /files/<filename>`

**Path Parameters:**
- `filename` (required): The name of the file to download

**Headers:**
- `Authorization: Bearer <token>` (required)

**Success Response (200 OK):**
- **Content-Type:** Varies based on file type (e.g., `application/pdf`, `image/png`)
- **Content-Disposition:** `attachment; filename="<filename>"`
- **Body:** Binary file content

**Error Responses:**

- **404 Not Found** - File does not exist
```json
{
  "success": false,
  "error": "File not found"
}
```

- **401 Unauthorized** - Invalid or missing JWT token
```json
{
  "msg": "Missing Authorization Header"
}
```

- **503 Service Unavailable** - Data service is down
```json
{
  "success": false,
  "error": "Service communication error: Connection refused"
}
```

---

## Error Handling

### Common Error Status Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Missing file, invalid parameters |
| 401 | Unauthorized | Missing/invalid JWT token, expired token |
| 404 | Not Found | File doesn't exist |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Backend service is down |

### Error Response Format

All errors follow this JSON structure:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

---

## Examples

### JavaScript/Fetch Examples

#### 1. Upload File

```javascript
async function uploadFile(file, token) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('https://localhost:7050/files/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const data = await response.json();
    
    if (data.success) {
      console.log('File uploaded successfully:', data.filename);
      return data;
    } else {
      console.error('Upload failed:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const token = localStorage.getItem('jwt_token');
  
  if (file && token) {
    await uploadFile(file, token);
  }
});
```

#### 2. List All Files

```javascript
async function getAllFiles(token) {
  try {
    const response = await fetch('https://localhost:7050/files', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    
    if (data.success) {
      console.log(`Found ${data.count} files:`, data.files);
      return data.files;
    } else {
      console.error('Failed to get files:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Error getting files:', error);
    throw error;
  }
}

// Usage
const token = localStorage.getItem('jwt_token');
const files = await getAllFiles(token);

// Display files in UI
files.forEach(filename => {
  console.log(`- ${filename}`);
});
```

#### 3. Download File

```javascript
async function downloadFile(filename, token) {
  try {
    const response = await fetch(`https://localhost:7050/files/${filename}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Download failed');
    }

    // Get the blob from response
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    console.log(`Downloaded: ${filename}`);
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
}

// Usage
const token = localStorage.getItem('jwt_token');
await downloadFile('document.pdf', token);
```

#### Complete React Component Example

```jsx
import React, { useState, useEffect } from 'react';

function FileManager() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const token = localStorage.getItem('jwt_token');

  // Load files on component mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const response = await fetch('https://localhost:7050/files', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setFiles(data.files);
      }
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://localhost:7050/files/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        alert('File uploaded successfully!');
        loadFiles(); // Refresh file list
      } else {
        alert(`Upload failed: ${data.error}`);
      }
    } catch (error) {
      alert(`Upload error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (filename) => {
    try {
      const response = await fetch(`https://localhost:7050/files/${filename}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert(`Download error: ${error.message}`);
    }
  };

  return (
    <div className="file-manager">
      <h2>File Manager</h2>
      
      {/* Upload Section */}
      <div className="upload-section">
        <input 
          type="file" 
          onChange={handleUpload} 
          disabled={uploading}
        />
        {uploading && <span>Uploading...</span>}
      </div>

      {/* File List */}
      <div className="file-list">
        <h3>Files ({files.length})</h3>
        <ul>
          {files.map((filename, index) => (
            <li key={index}>
              {filename}
              <button onClick={() => handleDownload(filename)}>
                Download
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default FileManager;
```

---

### cURL Examples

#### 1. Upload File

```bash
# Upload a PDF file
curl -X POST https://localhost:7050/files/upload \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@/path/to/document.pdf"

# Upload an image
curl -X POST https://localhost:7050/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.png"
```

#### 2. List All Files

```bash
curl https://localhost:7050/files \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Download File

```bash
# Download and save to current directory
curl https://localhost:7050/files/document.pdf \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o document.pdf

# Download with original filename
curl -OJ https://localhost:7050/files/report.xlsx \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Python Examples

```python
import requests

# Configuration
BASE_URL = "https://localhost:7050"
TOKEN = "your_jwt_token_here"

def upload_file(filepath):
    """Upload a file"""
    with open(filepath, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {TOKEN}'}
        
        response = requests.post(
            f'{BASE_URL}/files/upload',
            files=files,
            headers=headers,
            verify=False  # Only for development with self-signed certs
        )
        
        return response.json()

def get_all_files():
    """Get list of all files"""
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    response = requests.get(
        f'{BASE_URL}/files',
        headers=headers,
        verify=False
    )
    
    return response.json()

def download_file(filename, save_path):
    """Download a file"""
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    response = requests.get(
        f'{BASE_URL}/files/{filename}',
        headers=headers,
        verify=False
    )
    
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Error: {response.json()}")
        return False

# Usage examples
if __name__ == "__main__":
    # Upload
    result = upload_file('/path/to/document.pdf')
    print(f"Upload result: {result}")
    
    # List files
    files_data = get_all_files()
    print(f"Files: {files_data['files']}")
    
    # Download
    download_file('document.pdf', './downloaded_document.pdf')
```

---

## Best Practices

### 1. File Validation (Client-Side)

```javascript
function validateFile(file, maxSizeMB = 10) {
  // Check file size
  const maxSize = maxSizeMB * 1024 * 1024; // Convert to bytes
  if (file.size > maxSize) {
    throw new Error(`File size exceeds ${maxSizeMB}MB limit`);
  }

  // Check file type (example: only allow documents and images)
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('File type not allowed');
  }

  return true;
}

// Usage
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  try {
    validateFile(file);
    // Proceed with upload
  } catch (error) {
    alert(error.message);
  }
});
```

### 2. Progress Tracking

```javascript
async function uploadFileWithProgress(file, token, onProgress) {
  const formData = new FormData();
  formData.append('file', file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        onProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error('Upload failed'));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error'));
    });

    xhr.open('POST', 'https://localhost:7050/files/upload');
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}

// Usage
await uploadFileWithProgress(file, token, (progress) => {
  console.log(`Upload progress: ${progress.toFixed(2)}%`);
  // Update UI progress bar
});
```

### 3. Error Handling

```javascript
async function safeFileOperation(operation) {
  try {
    return await operation();
  } catch (error) {
    // Check for specific error types
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      // Token expired - redirect to login
      window.location.href = '/login';
    } else if (error.message.includes('503')) {
      // Service unavailable
      alert('Service temporarily unavailable. Please try again later.');
    } else {
      // General error
      alert(`Operation failed: ${error.message}`);
    }
    throw error;
  }
}

// Usage
await safeFileOperation(() => uploadFile(file, token));
```

### 4. Token Management

```javascript
// Store token after login
function storeToken(token) {
  localStorage.setItem('jwt_token', token);
  // Optional: Store expiration time
  const expiresAt = Date.now() + (24 * 60 * 60 * 1000); // 24 hours
  localStorage.setItem('token_expires_at', expiresAt);
}

// Get token with expiration check
function getToken() {
  const token = localStorage.getItem('jwt_token');
  const expiresAt = localStorage.getItem('token_expires_at');
  
  if (!token) return null;
  
  if (expiresAt && Date.now() > parseInt(expiresAt)) {
    // Token expired
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('token_expires_at');
    return null;
  }
  
  return token;
}

// Usage
const token = getToken();
if (!token) {
  window.location.href = '/login';
}
```

---

## Security Notes

1. **HTTPS Only**: Always use HTTPS in production to protect JWT tokens
2. **Token Storage**: Store JWT tokens securely (consider using httpOnly cookies for enhanced security)
3. **Token Expiration**: Implement token refresh logic for better UX
4. **File Validation**: Always validate file types and sizes on both client and server
5. **CORS**: The API allows all origins (`*`). In production, restrict to your frontend domain

---

## Support

For issues or questions:
- Check the [Error Handling](#error-handling) section
- Review the [Examples](#examples) for your use case
- Contact the backend team for API issues

**Last Updated:** December 8, 2024  
**API Version:** 1.0
