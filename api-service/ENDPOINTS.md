# API Endpoints Overview

This document provides a quick reference for the main API and WebSocket endpoints. For detailed flows, see `flow.md`.

---

## REST API Endpoints

### 1. `POST /api/v1/news/search`
- **Description:** Search news articles by user query.
- **Request:**
  ```json
  { "query": "string", "limit": 10 }
  ```
- **Response:**
  ```json
  {
    "results": [
      { "title": "string", "url": "string", "summary": "string", "published_at": "ISO8601 timestamp" }
    ]
  }
  ```
- **Errors:**
  - `400`: Invalid input
  - `500`: Server error
- **Auth:** JWT in `Authorization` header
- **Frontend Suggestions:**
  - Search bar with live suggestions
  - Paginated news results
  - Clickable article cards

---

## WebSocket Endpoint

### 2. `ws://<host>/ws/chat`
- **Description:** Real-time chat for user queries and bot responses.
- **Connection:**
  - JWT token as query param or header
- **Message Format:**
  ```json
  { "type": "user_message", "content": "string" }
  ```
- **Response Format:**
  ```json
  { "type": "bot_response", "content": "string" }
  ```
- **Error Format:**
  ```json
  { "type": "error", "message": "Details" }
  ```
- **Frontend Suggestions:**
  - Chat UI with typing indicator
  - Display bot and user messages distinctly
  - Error banners for connection issues

---

**General Notes:**
- All endpoints require JWT authentication.
- Use consistent error handling in the UI.
- Confirm request/response formats with backend before release. 