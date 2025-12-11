# Medical Records Bridge - Backend API

A FastAPI-based backend service for the Medical Records Bridge application. This API helps patients understand their medical data by providing secure storage of medical records and AI-powered translation of medical jargon into easy-to-understand language.

## Features

- **User Authentication**: Secure registration and login system with JWT token-based authentication
- **Medical Records Management**: Full CRUD operations for storing and managing medical records
- **AI-Powered Translation**: Convert medical terminology into layman's terms using Hugging Face Inference API (or local Ollama fallback)
- **Lifestyle Suggestions**: Generate personalized lifestyle tips based on medical conditions
- **User Dashboard**: Statistics and profile management
- **Interactive API Documentation**: Auto-generated Swagger UI and ReDoc documentation

## Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database (easily upgradeable to PostgreSQL)
- **Pydantic**: Data validation using Python type hints
- **JWT**: JSON Web Tokens for secure authentication
- **Bcrypt**: Password hashing
- **Hugging Face**: AI-powered medical text analysis (Primary)
- **Ollama**: Local fallback for AI services

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- (Optional) Hugging Face API Token (for primary AI features)
- (Optional) Ollama installed locally (for fallback AI features)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Required Settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./medical_records.db

# Optional: AI Features (Primary)
HUGGINGFACE_API_KEY=hf_your_token_here

# Optional: AI Features (Fallback)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 3. Run the Server

```bash
flask run
```

The server will start at `http://localhost:8000`

### Quick Start Script

Alternatively, use the quick start script:

```bash
chmod +x quickstart.sh
./quickstart.sh
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/me` - Get current user information (requires auth)

### Medical Records

- `POST /api/records` - Create a new medical record (requires auth)
- `GET /api/records` - List all user's medical records (requires auth)
- `GET /api/records/{id}` - Get specific medical record (requires auth)
- `PUT /api/records/{id}` - Update a medical record (requires auth)
- `DELETE /api/records/{id}` - Delete a medical record (requires auth)

### AI Services

- `POST /api/ai/translate` - Translate medical text to layman's terms (requires auth)
- `POST /api/ai/suggestions` - Get lifestyle suggestions for a condition (requires auth)
- `POST /api/ai/explain/{record_id}` - Get AI explanation for a medical record (requires auth)

### User Profile

- `GET /api/users/me` - Get user profile with statistics (requires auth)
- `PUT /api/users/me` - Update user profile (requires auth)
- `GET /api/users/dashboard` - Get dashboard statistics (requires auth)

## Usage Examples

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "username": "patient1",
    "password": "secure123",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=patient1&password=secure123"
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Create a Medical Record

```bash
curl -X POST "http://localhost:8000/api/records" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Blood Test Results",
    "original_text": "WBC: 7.5, RBC: 4.8, HGB: 14.2, PLT: 250",
    "record_type": "lab_result"
  }'
```

### Get AI Translation

```bash
curl -X POST "http://localhost:8000/api/ai/translate" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient presents with acute myalgia and pyrexia"
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup and session management
│   │
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py
│   │   └── medical_record.py
│   │
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── medical_record.py
│   │   └── auth.py
│   │
│   ├── api/
│   │   ├── deps.py          # Shared dependencies (auth, db)
│   │   └── routes/          # API route handlers
│   │       ├── auth.py
│   │       ├── medical_records.py
│   │       ├── ai.py
│   │       └── users.py
│   │
│   ├── services/            # Business logic layer
│   │   ├── auth.py
│   │   └── ai_service.py
│   │
│   └── utils/               # Utility functions
│       └── security.py
│
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── quickstart.sh           # Quick start setup script
└── README.md               # This file
```

## Environment Variables

### Required

- `SECRET_KEY` - Secret key for JWT token signing (use a long random string in production)
- `DATABASE_URL` - Database connection string (default: `sqlite:///./medical_records.db`)

### Optional

- `HUGGINGFACE_API_KEY` - Hugging Face user access token
- `HUGGINGFACE_MODEL` - Model to use (default: `meta-llama/Meta-Llama-3-8B-Instruct`)
- `HUGGINGFACE_BASE_URL` - API base URL (default: `https://api-inference.huggingface.co/models`)
- `OLLAMA_BASE_URL` - URL for local Ollama instance (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Local model to use (default: `llama3`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time (default: 30)
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins (default: localhost ports)

## Security Features

- **Password Hashing**: Bcrypt with salt for secure password storage
- **JWT Authentication**: Token-based authentication with expiration
- **Input Validation**: Pydantic schemas validate all input data
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Configurable cross-origin resource sharing

## Database

The application uses SQLite by default for easy setup and development. The database is automatically created on first run.

### Database Models

**User**
- id (Primary Key)
- email (Unique)
- username (Unique)
- hashed_password
- full_name
- created_at, updated_at

**MedicalRecord**
- id (Primary Key)
- user_id (Foreign Key)
- title
- original_text
- translated_text (cached AI translation)
- lifestyle_suggestions (cached AI suggestions)
- record_type
- created_at, updated_at

### Migrating to PostgreSQL

For production use, update your `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## AI Integration

The backend integrates with **Hugging Face Inference API** as the primary AI provider, with **Ollama** as a local fallback.

### How to obtain a Hugging Face Token (Quick Guide)

1.  **Sign Up/Log In**: Go to [huggingface.co](https://huggingface.co/).
2.  **Settings**: Click profile picture -> **Settings**.
3.  **Access Tokens**: Select **Access Tokens** from the sidebar.
4.  **Create Token**: Click **Create new token**, name it (e.g., `MedicalApp`), select **Read** permissions, and create.
5.  **Configure**: Copy the token (starts with `hf_`) and paste it into your `.env`:
    ```env
    HUGGINGFACE_API_KEY=hf_...
    ```

- **Medical Translation**: Converts complex medical terminology into simple language
- **Lifestyle Suggestions**: Generates personalized wellness tips (not medical advice)
- **Response Caching**: AI responses are cached in the database to reduce API calls

Note: The backend works without an API key if Ollama is running locally. If neither is available, AI features will be disabled.

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running in Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing Endpoints

Use the interactive Swagger UI at `/docs` or use curl/Postman to test endpoints manually.

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Database Errors**
- Delete `medical_records.db` and restart the server to recreate the database

**Authentication Errors**
- Ensure you're including the JWT token in the Authorization header: `Authorization: Bearer YOUR_TOKEN`

**AI Service Errors**
- Check that `HUGGINGFACE_API_KEY` is set in your `.env` file for remote inference
- For local fallback, ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3`)

## Notes

- This application is designed to help patients understand medical data
- It does NOT provide medical advice, diagnoses, or treatment recommendations
- Always consult qualified healthcare professionals for medical decisions
- User data is stored locally in the SQLite database

## Support

For issues or questions, please refer to the main project README or open an issue in the repository.

## License

This project is for educational purposes.
