# RAGSpace

A sophisticated RAG (Retrieval-Augmented Generation) platform built with a modern microservices architecture. This application enables users to upload documents, create workspaces, and interact with AI-powered chat to query their knowledge base using semantic search and LLM generation.

## 🏗️ Architecture Overview

The project consists of three main components working together:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (React + Vite)                    │
│                   (Port 5173 / Docker)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/CORS
┌─────────────────────────┴────────────────────────────────────┐
│              Node.js/Express Server (TypeScript)             │
│              (Port 3000 / Docker) - API Gateway              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Auth (JWT)                                         │   │
│  │ • User Management                                    │   │
│  │ • Workspace CRUD & Cascade Delete                    │   │
│  │ • Document Upload & Management                       │   │
│  │ • Chat Orchestration                                 │   │
│  │ • Redis Session Cache                                │   │
│  └──────────────────────────────────────────────────────┘   │
└──────┬───────────────────────────────────────────┬───────────┘
       │ HTTP Client                               │ MongoDB Driver
       │                                           │
┌──────┴──────────────────────┐        ┌──────────┴────────────┐
│ FastAPI Python AI Service   │        │  MongoDB (NoSQL)      │
│  (Port 8000 / Docker)       │        │  (Port 27017)         │
│ ┌──────────────────────────┐│        │                       │
│ │ • Document Parsing       ││        │ • Users Collection    │
│ │ • Text Chunking          ││        │ • Workspaces          │
│ │ • Embeddings (Gemini)    ││        │ • Documents           │
│ │ • Vector Storage         ││        │ • Chat Messages       │
│ │ • Semantic Retrieval     ││        │                       │
│ │ • LLM Response Gen       ││        │                       │
│ └──────────────────────────┘│        └───────────────────────┘
└─────────────────────────────┘
         │
         └─ File System
            (./server/uploads)
```

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Node.js** 18+ and **npm** (for local development)
- **Python** 3.9+ (for local development)
- **Gemini API Key** (for AI features)

### Setup with Docker (Recommended)

#### 1. Environment Configuration

Create `.env` files in the following locations:

**`server/.env`**

```
# Server Configuration
PORT=3000
NODE_ENV=development
LOG_LEVEL=debug

# Database
MONGO_URI=mongodb://mongo:27017/ai_knowledge_workspace

# Redis
REDIS_URL=redis://redis:6379

# JWT
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
JWT_EXPIRY=7d

# Python AI Service
PYTHON_AI_BASE_URL=http://python-ai:8000

# CORS
CORS_ORIGIN=http://localhost:5173
```

**`python-ai/.env`**

```
# Python AI Service
ENVIRONMENT=development
LOG_LEVEL=debug

# Gemini Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Database
MONGO_URI=mongodb://mongo:27017/ai_knowledge_workspace

# File paths
UPLOAD_DIR=/app/uploads
```

**`client/.env`** (if needed for runtime)

```
VITE_API_BASE_URL=http://localhost:3000
```

#### 2. Start with Docker Compose

```bash
cd AI-Knowledge-Workspace
docker-compose up --build
```

**Service URLs:**

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:3000`
- Python AI Service: `http://localhost:8000`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`

#### 3. Verify Services

```bash
# Check all containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Development Setup

#### Client Setup

```bash
cd client

# Install dependencies
npm install

# Start development server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### Server Setup

```bash
cd server

# Install dependencies
npm install

# Start development server (port 3000)
# Requires MongoDB and Redis running locally
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test
```

#### Python AI Service Setup

```bash
cd python-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt

# Start development server (port 8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest -v
```

## 📋 Complete Workflow

### 1. **Authentication Flow**

```
User Signup/Login
      ↓
Express Server validates credentials (bcryptjs)
      ↓
MongoDB stores user record
      ↓
JWT token generated & returned
      ↓
Token stored in browser (cookies/localStorage)
      ↓
All subsequent requests include token (ProtectedRoute)
```

**Files involved:**

- Client: [src/pages/Login.tsx](client/src/pages/Login.tsx), [src/pages/Signup.tsx](client/src/pages/Signup.tsx)
- Server: [src/modules/auth/](server/src/modules/auth/)

### 2. **Workspace Management**

```
User Creates Workspace
      ↓
Server validates input (Zod schema)
      ↓
MongoDB creates workspace doc with userId
      ↓
Workspace returned to client
      ↓
User can add/view/edit/delete workspaces
      ↓
Cascade delete: removing workspace removes all its documents
```

**Files involved:**

- Client: [src/pages/Workspaces.tsx](client/src/pages/Workspaces.tsx)
- Server: [src/modules/workspaces/](server/src/modules/workspaces/)
- Tests: [tests/workspace.service.test.ts](server/tests/workspace.service.test.ts)

### 3. **Document Upload & Processing**

```
User Selects File in Workspace
      ↓
Client sends multipart/form-data to server
      ↓
Server validates (multer middleware)
      ↓
File saved to ./server/uploads/
      ↓
Server returns file metadata to client
      ↓
Server sends document to Python AI Service
      ↓
Python service:
  • Parses file (PDF/DOCX)
  • Chunks text into manageable pieces
  • Generates embeddings via Gemini API
  • Stores in MongoDB (vectorized)
      ↓
Document indexed and ready for queries
```

**Files involved:**

- Client: [src/api/documents.ts](client/src/api/documents.ts)
- Server: [src/modules/documents/](server/src/modules/documents/), [src/middleware/upload.middleware.ts](server/src/middleware/upload.middleware.ts)
- Python: [app/routers/index_document.py](python-ai/app/routers/index_document.py), [app/services/](python-ai/app/services/)
- Tests: [tests/document.upload.integration.test.ts](server/tests/document.upload.integration.test.ts)

### 4. **Semantic Search & Retrieval**

```
User Submits Query
      ↓
Client sends message to server
      ↓
Server saves message to MongoDB (chat collection)
      ↓
Server forwards query to Python AI Service
      ↓
Python service:
  • Generates embedding for user query
  • Searches MongoDB vectors (semantic similarity)
  • Retrieves top-K relevant chunks
  • Constructs context from retrieved docs
      ↓
Retrieved context returned to server
```

**Files involved:**

- Server: [src/modules/chat/chat.service.ts](server/src/modules/chat/chat.service.ts)
- Python: [app/routers/query.py](python-ai/app/routers/query.py), [app/services/retrieval.py](python-ai/app/services/retrieval.py)

### 5. **Chat & LLM Generation**

```
Retrieved Context from Search
      ↓
Server receives context + query
      ↓
Server calls Python AI Service for generation
      ↓
Python service:
  • Constructs prompt with context
  • Calls Gemini LLM API
  • Streams/returns response
      ↓
Server adds AI response to MongoDB (chat record)
      ↓
Response sent to client
      ↓
Client displays message in real-time
```

**Files involved:**

- Server: [src/modules/chat/chat.controller.ts](server/src/modules/chat/chat.controller.ts)
- Python: [app/routers/query.py](python-ai/app/routers/query.py), [app/services/generation.py](python-ai/app/services/generation.py)
- Client: [src/pages/Chat.tsx](client/src/pages/Chat.tsx)

### 6. **Dashboard & Analytics**

```
User Visits Dashboard
      ↓
Server queries MongoDB:
  • Count workspaces
  • Count documents per workspace
  • Recent chat messages
  • User statistics
      ↓
Data aggregated and formatted
      ↓
Dashboard displays metrics & insights
```

**Files involved:**

- Client: [src/pages/Dashboard.tsx](client/src/pages/Dashboard.tsx)
- Server: [src/modules/dashboard/](server/src/modules/dashboard/)

## 📁 Project Structure

```
AI-Knowledge-Workspace/
├── docker-compose.yml           # Service orchestration
├── client/                       # React frontend (Vite + TypeScript)
│   ├── src/
│   │   ├── pages/               # Page components (Login, Chat, Dashboard, etc.)
│   │   ├── components/          # Reusable components (NavBar, ProtectedRoute)
│   │   ├── api/                 # API client functions (auth, chat, documents)
│   │   ├── lib/                 # Context & utilities (AuthProvider)
│   │   └── styles/              # Tailwind CSS
│   └── package.json
│
├── server/                       # Node.js Express backend (TypeScript)
│   ├── src/
│   │   ├── modules/             # Feature modules
│   │   │   ├── auth/            # Authentication (login, signup, JWT)
│   │   │   ├── workspaces/      # Workspace CRUD
│   │   │   ├── documents/       # Document management
│   │   │   └── chat/            # Chat orchestration
│   │   ├── middleware/          # Express middleware (auth, error, upload)
│   │   ├── config/              # Configuration (DB, Redis, env)
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Utilities (JWT, logger, error handling)
│   │   ├── app.ts               # Express app setup
│   │   └── server.ts            # Entry point
│   ├── tests/                   # Unit & integration tests
│   ├── uploads/                 # User uploaded files (shared with Python)
│   └── package.json
│
├── python-ai/                    # FastAPI AI service (Python)
│   ├── app/
│   │   ├── routers/             # API endpoints
│   │   │   ├── health.py        # Health check
│   │   │   ├── index_document.py # Document indexing
│   │   │   └── query.py         # Query & generation
│   │   ├── services/            # Business logic
│   │   │   ├── parsing.py       # PDF/DOCX parsing
│   │   │   ├── chunking.py      # Text chunking
│   │   │   ├── embeddings.py    # Gemini embeddings
│   │   │   ├── retrieval.py     # Vector search
│   │   │   ├── indexing.py      # MongoDB indexing
│   │   │   └── generation.py    # LLM response generation
│   │   ├── db/
│   │   │   └── mongo.py         # MongoDB connection & indexes
│   │   ├── providers/           # AI providers (Gemini)
│   │   ├── core/
│   │   │   └── config.py        # Configuration
│   │   └── main.py              # FastAPI app setup
│   ├── tests/                   # Unit tests
│   └── requirements.txt
```

## 🔌 API Endpoints

### Authentication

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Workspaces

- `GET /api/workspaces` - List user workspaces
- `POST /api/workspaces` - Create workspace
- `GET /api/workspaces/:id` - Get workspace details
- `PUT /api/workspaces/:id` - Update workspace
- `DELETE /api/workspaces/:id` - Delete workspace (cascades)

### Documents

- `POST /api/workspaces/:workspaceId/documents` - Upload document
- `GET /api/workspaces/:workspaceId/documents` - List documents
- `DELETE /api/documents/:documentId` - Delete document

### Chat

- `GET /api/workspaces/:workspaceId/messages` - Get chat history
- `POST /api/workspaces/:workspaceId/messages` - Send message & get AI response

### Dashboard

- `GET /api/dashboard/stats` - Get user statistics

### Python AI Service

- `GET /health` - Health check
- `POST /index-document` - Index uploaded document
- `POST /query` - Query & generate response

## 🛠️ Technologies Used

### Frontend

- **React 18** - UI library
- **Vite** - Fast bundler
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching & caching
- **Tailwind CSS** - Styling

### Backend (Node.js)

- **Express.js** - Web framework
- **TypeScript** - Type safety
- **Mongoose** - MongoDB ODM
- **JSON Web Tokens (JWT)** - Authentication
- **bcryptjs** - Password hashing
- **ioredis** - Redis client
- **Multer** - File upload middleware
- **Jest** - Testing framework

### AI Service (Python)

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **PyMongo/Motor** - MongoDB async driver
- **Google Generative AI** - Gemini embeddings & LLM
- **pypdf/python-docx** - Document parsing
- **pytest** - Testing framework

### Infrastructure

- **Docker & Docker Compose** - Containerization
- **MongoDB 7** - NoSQL database (vectors, chat history, users)
- **Redis 7** - In-memory cache & session store
- **Nginx** - Reverse proxy (client)

## 📊 Database Schema

### MongoDB Collections

**users**

```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  name: String,
  createdAt: Date,
  updatedAt: Date
}
```

**workspaces**

```javascript
{
  _id: ObjectId,
  userId: ObjectId (ref: users),
  name: String,
  description: String,
  createdAt: Date,
  updatedAt: Date
}
```

**documents**

```javascript
{
  _id: ObjectId,
  workspaceId: ObjectId (ref: workspaces),
  fileName: String,
  fileSize: Number,
  filePath: String,
  chunks: [
    {
      chunkId: String,
      text: String,
      embedding: Array<Number>,  // Vector from Gemini
      pageNumber: Number
    }
  ],
  createdAt: Date,
  updatedAt: Date
}
```

**messages** (chat)

```javascript
{
  _id: ObjectId,
  workspaceId: ObjectId (ref: workspaces),
  userId: ObjectId (ref: users),
  userMessage: String,
  aiResponse: String,
  retrievedContext: [String],  // Chunks used for response
  createdAt: Date
}
```

## 🧪 Testing

### Run Server Tests

```bash
cd server
npm test
```

**Test files:**

- `test_api.py` - API endpoints
- `test_chunking.py` - Text chunking logic
- `test_indexing.py` - Document indexing
- `test_retrieval_generation.py` - Semantic search & LLM

### Run Python Tests

```bash
cd python-ai
pytest -v
```

## 🔐 Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - bcryptjs with salt rounds
- **CORS Protection** - Configured origin allowlist
- **Helmet** - Security headers
- **Input Validation** - Zod schema validation (server), Pydantic (Python)
- **Error Middleware** - Safe error messages (no sensitive data leakage)
- **Protected Routes** - Client-side route protection
- **File Upload Validation** - File type & size restrictions

## 📝 Environment Variables Reference

| Variable             | Location       | Description                          |
| -------------------- | -------------- | ------------------------------------ |
| `PORT`               | server/.env    | Express server port (default: 3000)  |
| `NODE_ENV`           | server/.env    | Environment (development/production) |
| `MONGO_URI`          | Both .env      | MongoDB connection string            |
| `REDIS_URL`          | server/.env    | Redis connection URL                 |
| `JWT_SECRET`         | server/.env    | Secret key for JWT signing           |
| `GOOGLE_API_KEY`     | python-ai/.env | Gemini API key for embeddings & LLM  |
| `PYTHON_AI_BASE_URL` | server/.env    | URL of Python AI service             |
| `CORS_ORIGIN`        | server/.env    | Allowed frontend URL                 |

## 🚨 Common Issues & Troubleshooting

### MongoDB Connection Error

```
Error: connect ECONNREFUSED 127.0.0.1:27017
```

**Solution:** Ensure MongoDB is running via Docker or locally. Check `MONGO_URI` in `.env`.

### Python Service Timeout

```
Error: HTTPError: 503 Service Unavailable
```

**Solution:** Ensure Python service is running and `PYTHON_AI_BASE_URL` is correct.

### File Upload Fails

```
Error: ENOENT: no such file or directory ./server/uploads
```

**Solution:** Create the uploads directory:

```bash
mkdir -p server/uploads
```

### JWT Token Expired

**Solution:** User needs to login again. Token expiry is set in `JWT_EXPIRY`.

### Document Embedding Takes Too Long

**Solution:** Large documents may take time to chunk & embed. Check Python logs:

```bash
docker-compose logs python-ai
```

## 📈 Performance Optimization

- **Vector Indexes:** MongoDB automatically optimizes vector searches
- **Redis Caching:** Session & frequently accessed data cached
- **Pagination:** Large result sets paginated
- **Lazy Loading:** Client-side route lazy loading
- **Compression:** Gzip enabled in Express

## 📚 Additional Resources

- [MongoDB Vectors Documentation](https://www.mongodb.com/docs/manual/core/vectors/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express.js Documentation](https://expressjs.com/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit: `git commit -m 'Add my feature'`
3. Push to the branch: `git push origin feature/my-feature`
4. Open a pull request

## 📄 License

This project is licensed under the MIT License.

## 📧 Support

For issues, questions, or suggestions, please create an issue in the repository.

---

**Last Updated:** 2026-07-07  
**Version:** 1.0.0
