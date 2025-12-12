# Medical Records Bridge

A comprehensive application that bridges the gap between patients and medical professionals by streamlining access to medical records and helping patients understand their medical data using AI.

## Features

- **User Authentication**: Secure registration and login system with JWT tokens
- **Medical Records Management**: Upload, store, and manage medical records (doctor's notes, lab results, prescriptions)
- **AI-Powered Translation**: Convert medical jargon into easy-to-understand language using Meta AI (Llama models)
- **Lifestyle Suggestions**: Get personalized lifestyle tips tailored to specific medical conditions
- **Dashboard**: View statistics and recent medical records
- **Secure & Private**: User data is protected with industry-standard security practices

## Tech Stack

### Backend
- **Flask**: Lightweight and flexible web framework with excellent extension support
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Production-grade relational database
- **Marshmallow**: Data serialization and validation
- **Flask-JWT-Extended**: JWT-based authentication
- **Groq AI**: Fast AI inference (Primary)
- **Hugging Face**: AI model fallback
- **Ollama**: Local AI inference (Fallback)

### Frontend
- Coming soon...

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- `python3.10-venv` package (for virtual environments)
- PostgreSQL 12+ installed and running
- (Optional) Groq API key for AI features
- (Optional) Hugging Face API token for AI fallback

## Setup Instructions

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meta-hack
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Install venv package (Ubuntu/Debian)**
   ```bash
   sudo apt install python3.10-venv
   ```

4. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate on Linux/Mac
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For testing
   ```

6. **Set up PostgreSQL database**
   ```bash
   # Create PostgreSQL user and database
   sudo -u postgres createuser -s medbridge
   sudo -u postgres createdb -O medbridge medbridge
   ```

7. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and configure:
   # - DATABASE_URL (PostgreSQL connection)
   # - GROQ_API_KEY (for AI features)
   # - HUGGINGFACE_API_KEY (optional fallback)
   ```

8. **Seed the database (optional)**
   ```bash
   make seed
   ```

9. **Run the application**
   ```bash
   flask run
   # Or use make:
   make run
   ```

   The API will be available at `http://localhost:5000`

10. **Access API Documentation**
   - Swagger UI: `http://localhost:5000/apidocs`

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Security
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (PostgreSQL)
DATABASE_URL=postgresql://medbridge@localhost:5432/medbridge

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
HUGGINGFACE_API_KEY=your-hf-token-here  # Optional fallback
OLLAMA_BASE_URL=http://localhost:11434  # Local fallback
```

### Getting AI API Keys

**Groq (Primary - Fast & Free)**
1. Sign up at [Groq Console](https://console.groq.com/)
2. Navigate to API Keys
3. Create new key and add to `.env`

**Hugging Face (Fallback - Optional)**
1. Sign up at [Hugging Face](https://huggingface.co/)
2. Go to Settings → Access Tokens
3. Create token and add to `.env`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Medical Records
- `POST /api/records` - Create a new medical record
- `GET /api/records` - List all user's medical records
- `GET /api/records/{id}` - Get specific medical record
- `PUT /api/records/{id}` - Update a medical record
- `DELETE /api/records/{id}` - Delete a medical record

### AI Services
- `POST /api/ai/translate` - Translate medical text to layman's terms
- `POST /api/ai/suggestions` - Get lifestyle suggestions for a condition
- `POST /api/ai/explain/{record_id}` - Get AI explanation for a medical record

### User Profile
- `GET /api/users/me` - Get user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users/dashboard` - Get dashboard statistics

## Testing the API

1. **Register a user**
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

2. **Login**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=patient1&password=secure123"
   ```

3. **Use the interactive docs**
   - Visit `http://localhost:8000/docs`
   - Click "Authorize" and enter your token
   - Test all endpoints interactively

## Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-auth
make test-ai
make test-records
make test-users
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   └── medical_record.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── medical_record.py
│   │   └── auth.py
│   ├── api/
│   │   ├── deps.py          # Dependencies (auth, db)
│   │   └── routes/          # API routes
│   │       ├── auth.py
│   │       ├── medical_records.py
│   │       ├── ai.py
│   │       └── users.py
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   └── ai_service.py
│   └── utils/
│       └── security.py      # Security utilities
├── requirements.txt
├── .env.example
└── .gitignore
```

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Token expiration
- CORS configuration
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

## Future Enhancements

- [ ] OCR support for scanned documents
- [ ] File upload for images (doctor's notes, lab results)
- [ ] Export medical records as PDF
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Integration with health tracking devices
- [ ] Appointment scheduling

## License

This project is for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue in the repository.

---

**Note**: This application is designed to help patients understand their medical data. It does NOT provide medical advice, diagnoses, or treatment recommendations. Always consult with qualified healthcare professionals for medical decisions.