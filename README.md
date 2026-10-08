# Full-Stack AI Todo List Application

A complete, working Todo List web application with AI-powered task suggestions, built with Next.js, FastAPI, and MongoDB Atlas.

## Features

- **Task Management**: Create, read, update, delete, complete, and uncomplete tasks
- **Page/Project System**: Organize tasks into pages/projects with duplicate prevention
- **Search**: Search tasks by title and description
- **Filtering**: Filter by All, Pending, or Completed status
- **Sorting**: Sort by newest, oldest, or recently updated
- **AI Assistant**: Get AI-powered task suggestions using Agno + LiteLLM
- **Responsive Design**: Works on desktop, laptop, tablet, and mobile
- **Modern UI**: Clean, professional design with Tailwind CSS
- **Real-time Updates**: No page refresh needed for most operations
- **Error Handling**: User-friendly error messages throughout

## Architecture

```
┌─────────────────────┐
│      NEXT.JS        │
│ React + Tailwind CSS │
│      FRONTEND       │
└──────────┬──────────┘
           │
     REST API / HTTP
           │
           ▼
┌─────────────────────┐
│       FASTAPI       │
│       BACKEND       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    MONGODB ATLAS    │
│      DATABASE       │
└─────────────────────┘

          +
    Agno + LiteLLM
      AI Assistant
```

## Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **Tailwind CSS 4** - Utility-first CSS framework

### Backend
- **Python 3.12+** - Programming language
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **PyMongo** - MongoDB driver

### Database
- **MongoDB Atlas** - Cloud database service

### AI
- **Agno** - AI agent framework
- **LiteLLM** - LLM API proxy (supports OpenAI, Anthropic, etc.)

## Folder Structure

```
todo-app/
│
├── frontend/
│   ├── app/
│   │   ├── layout.js          # Root layout
│   │   ├── page.js            # Main page (Dashboard)
│   │   └── globals.css        # Global styles
│   │
│   ├── components/
│   │   ├── Sidebar.js         # Sidebar with pages list
│   │   ├── Header.js          # Top header bar
│   │   ├── TodoList.js        # Task list container
│   │   ├── TodoItem.js        # Individual task card
│   │   ├── AddTaskModal.js    # Add task modal
│   │   ├── EditTaskModal.js   # Edit task modal
│   │   ├── SearchBar.js       # Search input
│   │   └── AIChat.js          # AI assistant chat
│   │
│   ├── services/
│   │   └── api.js             # API service functions
│   │
│   ├── public/                # Static assets
│   ├── .env.local             # Frontend environment variables
│   ├── package.json
│   ├── next.config.js
│   ├── postcss.config.js
│   └── .gitignore
│
├── backend/
│   ├── main.py                # FastAPI application entry point
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb.py         # MongoDB connection module
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py            # Task Pydantic models
│   │   └── page.py            # Page Pydantic models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py           # Task API endpoints
│   │   ├── pages.py           # Page API endpoints
│   │   └── ai.py              # AI API endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py    # Task business logic
│   │   ├── page_service.py    # Page business logic
│   │   └── ai_service.py      # AI business logic
│   │
│   ├── .env                   # Backend environment variables
│   ├── requirements.txt       # Python dependencies
│   └── .gitignore
│
└── README.md
```

## Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **MongoDB Atlas Account** - [Sign up free](https://www.mongodb.com/cloud/atlas)
- **OpenAI API Key** (optional, for AI features) - [Get key](https://platform.openai.com/api-keys)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd todo-app
```

### 2. Set Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account
2. Create a new cluster (the free M0 tier is sufficient)
3. Click "Database Access" → "Add New Database User"
   - Username: `todoapp`
   - Password: (choose a secure password)
   - Privileges: "Read and write to any database"
4. Click "Network Access" → "Add IP Address"
   - Allow access from anywhere: `0.0.0.0/0` (for development only)
5. Click "Connect" → "Connect your application"
6. Copy the connection string, it looks like:
   ```
   mongodb+srv://todoapp:<password>@cluster0.xxxxx.mongodb.net/
   ```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Backend Environment Variables

Edit `backend/.env`:

```env
MONGO_CONNECTION_STRING=mongodb+srv://todoapp:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=todo_db
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Important**: Replace `YOUR_PASSWORD` with your actual MongoDB password and `cluster0.xxxxx` with your cluster name.

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 6. Configure Frontend Environment Variables

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## How to Run

### Start the Backend

Open a terminal and run:

```bash
cd backend
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
uvicorn main:app --reload
```

The backend will start at `http://127.0.0.1:8000`

Verify it's working:
- API Docs (Swagger): http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

### Start the Frontend

Open a **new** terminal and run:

```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:3000`

Open your browser and go to: **http://localhost:3000**

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | Get all tasks (supports `?page=`, `?status=`, `?search=`) |
| GET | `/tasks/{task_id}` | Get a single task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update a task |
| PATCH | `/tasks/{task_id}/complete` | Mark task as completed |
| PATCH | `/tasks/{task_id}/uncomplete` | Mark task as pending |
| DELETE | `/tasks/{task_id}` | Delete a task |
| DELETE | `/tasks/completed/clear` | Delete all completed tasks |

### Pages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pages` | Get all pages |
| POST | `/pages` | Create a new page |
| DELETE | `/pages/{page_id}` | Delete a page |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/suggest-tasks` | Get AI task suggestions |
| GET | `/ai/status` | Check AI configuration status |

## AI Setup (Optional)

The AI assistant uses OpenAI through LiteLLM. To enable it:

1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Add it to `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Restart the backend

If AI is not configured, the Todo application still works perfectly. The AI Assistant button will show a configuration message.

## Troubleshooting

### Backend won't start
- Make sure Python 3.12+ is installed: `python --version`
- Make sure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`

### MongoDB connection error
- Verify your connection string in `backend/.env`
- Make sure your IP is whitelisted in MongoDB Atlas Network Access
- Check that the database user has correct permissions

### Frontend can't connect to backend
- Make sure the backend is running on port 8000
- Check `frontend/.env.local` has the correct API URL
- Open browser console (F12) to see error details

### CORS errors
- The backend already allows `http://localhost:3000` and `http://127.0.0.1:3000`
- If using a different port, update `backend/main.py` CORS settings

### AI not working
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Check that the key is valid and has credits
- The app works without AI - this is optional

## Development

### Project Structure
- **Frontend**: Next.js App Router with React Server Components
- **Backend**: FastAPI with clean separation (Routes → Services → Database)
- **Database**: MongoDB Atlas with PyMongo

### Adding New Features
1. Add Pydantic models in `backend/models/`
2. Add business logic in `backend/services/`
3. Add API endpoints in `backend/routes/`
4. Add API functions in `frontend/services/api.js`
5. Add UI components in `frontend/components/`

## License

MIT License - feel free to use this project for learning or as a template.
