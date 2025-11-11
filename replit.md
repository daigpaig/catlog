# Academic Course Scheduler

## Overview
A full-stack web application for academic course scheduling, featuring an AI-powered chat assistant to help students plan their schedules. Built with React + TypeScript (Vite) frontend and FastAPI Python backend.

## Project Status
- **Current State**: Development environment configured and running
- **Last Updated**: November 11, 2025
- **Frontend**: Running on port 5000 (configured for Replit proxy)
- **Backend**: FastAPI server (not currently running, ready to deploy on port 8000)

## Architecture

### Frontend (React + Vite + TypeScript)
- **Location**: `/frontend`
- **Port**: 5000 (configured for Replit environment)
- **Key Features**:
  - Weekly calendar view for course scheduling
  - Student profile management
  - AI chat assistant for schedule recommendations
  - Responsive UI with Tailwind CSS and Radix UI components

### Backend (FastAPI + Python)
- **Location**: `/backend`
- **Port**: 8000 (localhost only)
- **Dependencies**: FastAPI, SQLModel, OpenAI, Pandas, PDFPlumber
- **Key Features**:
  - Chat endpoint for AI-powered scheduling assistance
  - User profile management
  - Schedule CRUD operations
  - Course catalog scraping utilities

## Technology Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, React Router
- **Backend**: Python 3.11, FastAPI, SQLModel, OpenAI API
- **Database**: SQLite (development)
- **Deployment**: Configured for Replit autoscale deployment

## Configuration

### Environment Setup
- Python 3.11 with uv package manager
- Node.js 20 with npm
- Vite configured for Replit proxy (host 0.0.0.0, port 5000)

### API Configuration
The frontend uses dynamic API URL configuration (`frontend/src/config/api.ts`):
- Development: `http://localhost:8000`
- Production: Automatically detects Replit domain

## Development

### Running the Project
The frontend workflow is configured to start automatically:
```bash
cd frontend && npm run dev
```

To run the backend separately:
```bash
cd backend && uvicorn app.main:app --host localhost --port 8000 --reload
```

### Key Files
- `frontend/vite.config.ts`: Vite configuration with Replit proxy support
- `frontend/src/config/api.ts`: Dynamic API URL configuration
- `backend/app/main.py`: FastAPI application entry point
- `backend/requirements.txt`: Python dependencies

## Deployment
Configured for Replit autoscale deployment:
- Build: Frontend npm install
- Run: Vite preview on port 5000

## Notes
- Sample data has been generalized for portfolio presentation
- Backend dependencies tracked via pyproject.toml and uv.lock
- Database files excluded from version control
