# Medical Records Bridge

A comprehensive application that bridges the gap between patients and medical professionals by streamlining access to medical records and helping patients understand their medical data using AI.

##Features

- **User Authentication**: Secure registration and login system with JWT tokens
- **Medical Records Management**: Upload, store, and manage medical records (doctor's notes, lab results, prescriptions)
- **AI-Powered Translation**: Convert medical jargon into easy-to-understand language using Meta AI (Llama models)
- **Lifestyle Suggestions**: Get personalized lifestyle tips tailored to specific medical conditions
- **Dashboard**: View statistics and recent medical records
- **Secure & Private**: User data is protected with industry-standard security practices

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (development) - easily upgradeable to PostgreSQL for production
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Secure authentication with JSON Web Tokens
- **Meta AI (Llama)**: AI-powered medical text translation via Together AI API

### Frontend
- Coming soon...

##  Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment tool (venv)
- Meta AI API key (get from [Together AI](https://api.together.xyz/))

##  Setup Instructions

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

3. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Linux/Mac
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your configuration
   # Most importantly, add your META_AI_API_KEY
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

7. **Access API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./medical_records.db

# Meta AI Configuration (Together AI)
META_AI_API_KEY=your-together-ai-api-key-here
META_AI_MODEL=meta-llama/Llama-3-70b-chat-hf
META_AI_BASE_URL=https://api.together.xyz/v1
```

### Getting Meta AI API Key

1. Sign up at [Together AI](https://api.together.xyz/)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key and add it to your `.env` file

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

##️ Project Structure

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