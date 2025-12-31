# Northwestern Course AI

An intelligent course scheduling assistant for Northwestern University students that leverages AI to provide personalized course recommendations and academic planning guidance.

## Purpose

Course selection at Northwestern can be overwhelming with hundreds of courses, complex prerequisites, and distribution requirements. This application simplifies the process by providing an AI-powered conversational interface that understands your academic profile, preferences, and goals to help you make informed course decisions.

## Features

### Current Implementation

- **AI-Powered Chat Interface**: Natural language conversations with GPT-4o to get course recommendations, descriptions, and academic advice
- **User Authentication**: Secure JWT-based authentication with email/password and Google OAuth support
- **Personalized User Profiles**: Store academic information including:
  - Majors and minors
  - Completed courses
  - Vocational interests
  - Professor preferences
  - Scheduling constraints (earliest class time, locked classes)
  - Self-description for personalized recommendations
- **Interactive Schedule Builder**: Visual weekly calendar interface for planning your course schedule
- **Course Catalog Integration**: Built on the [paper.nu API](https://paper.nu) (created by former Northwestern student Dilan) for comprehensive course catalog data
- **Program Requirements Database**: Structured data for major/minor requirements and prerequisites

### In Development

- Vector database integration (Chroma) for semantic course search
- Real-time schedule conflict detection
- Prerequisite validation
- Distribution requirement tracking
- Course recommendation engine with RAG (Retrieval-Augmented Generation)
- Export schedules to various formats

## Architecture

### Tech Stack

**Backend:**

- **FastAPI** - Modern Python web framework for building REST APIs
- **SQLModel** - SQL database ORM with Pydantic integration
- **SQLite** - Lightweight database for development
- **OpenAI GPT-4o** - Large language model for conversational AI
- **JWT** - Stateless authentication with access and refresh tokens
- **Bcrypt** - Secure password hashing
- **Pydantic** - Data validation and settings management

**Frontend:**

- **React 19** - UI library with TypeScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Radix UI** - Accessible component primitives

**Data Processing:**

- **BeautifulSoup4** - Web scraping for course catalog
- **PDFplumber** - PDF parsing for course requirements
- **Pandas** - Data manipulation and analysis

### Project Structure

```
northwestern-course-ai/
├── backend/
│   ├── app/
│   │   ├── auth/              # Authentication module
│   │   │   ├── router.py      # Auth endpoints (login, register, refresh)
│   │   │   ├── security.py    # JWT & password hashing
│   │   │   ├── dependencies.py # Auth middleware
│   │   │   └── google_oauth.py # Google OAuth integration
│   │   ├── routers/            # API route handlers
│   │   │   ├── chat.py        # AI chat endpoint
│   │   │   ├── user.py        # User profile management
│   │   │   └── schedule.py    # Schedule CRUD operations
│   │   ├── services/          # Business logic
│   │   │   ├── openai_service.py    # GPT-4o integration
│   │   │   ├── db_service.py         # Database operations
│   │   │   └── prompt_builder.py     # Context building for AI
│   │   ├── models/            # Database models (SQLModel)
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── config/            # Configuration management
│   │   ├── scrapers/          # Course catalog scraping tools
│   │   └── main.py            # FastAPI application entry point
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ChatWindow.tsx      # AI chat interface
│   │   │   ├── WeeklyCalendar.tsx  # Schedule visualization
│   │   │   └── ui/            # Reusable UI components
│   │   ├── pages/             # Page components
│   │   │   ├── Home.tsx       # Main application page
│   │   │   ├── Profile.tsx    # User profile management
│   │   │   └── Login.tsx      # Authentication page
│   │   ├── contexts/          # React context providers
│   │   │   └── AuthContext.tsx # Global auth state
│   │   ├── services/          # API client
│   │   │   └── api.ts         # Centralized API service
│   │   └── config/            # Configuration
│   └── package.json           # Node.js dependencies
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- (Optional) Google OAuth credentials for Google Sign-In

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLIENT_ID=your-google-client-id  # Optional
GOOGLE_CLIENT_SECRET=your-google-client-secret  # Optional
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback  # Optional
```

5. Initialize the database:

```bash
python -m app.database init_db
# Or run the migration script:
python scripts/migrate_db.py
```

6. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id  # Optional
```

4. Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Documentation

Once the backend is running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

**Authentication:**

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email/password
- `POST /auth/google/callback` - Google OAuth callback
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

**Chat:**

- `POST /chat` - Send message to AI assistant (requires authentication)

**Profile:**

- `GET /profile/me` - Get current user's profile
- `PUT /profile/me` - Update current user's profile

**Schedule:**

- `GET /schedule` - Get all schedules for current user
- `POST /schedule` - Create a new schedule
- `GET /schedule/{id}` - Get a specific schedule
- `DELETE /schedule/{id}` - Delete a schedule

## Security Features

- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- CORS middleware for secure cross-origin requests
- Protected routes requiring authentication
- Secure token storage in localStorage (consider httpOnly cookies for production)

## Academic Data

The application leverages:

- **paper.nu API**: Course catalog data provided by [paper.nu](https://paper.nu), a project created by former Northwestern student Dilan
- Program requirements database (majors, minors, certificates)
- Course descriptions, prerequisites, and scheduling information

## Development Status

This project is currently in active development. Core features are implemented and functional, but several enhancements are planned:

- [ ] Vector database integration for semantic course search
- [ ] Real-time conflict detection
- [ ] Automated prerequisite checking
- [ ] Distribution requirement tracking
- [ ] Enhanced AI recommendations with RAG
- [ ] Schedule export functionality
- [ ] Mobile-responsive design improvements
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

This project is for educational and personal use.

## Acknowledgments

- **Dilan** - Creator of [paper.nu](https://paper.nu), which provides the course catalog API that powers this application
- Northwestern University for course catalog data
- OpenAI for GPT-4o API
- The open-source community for excellent tools and libraries

---

**Note**: This application is not officially affiliated with Northwestern University. It is an independent project created to help students with course planning.
