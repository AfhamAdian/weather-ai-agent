# Project Name

A full-stack application powered by a FASTAPI backend and a React frontend.

---

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_folder>
```

---

## Backend Setup (agent-server)

### Step 1: Environment Setup

```bash
cd agent-server

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Variables

Create a `.env` file inside the `agent-server` directory with the following contents:

```
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Replace the placeholders with your actual API keys.

### Step 3: Run the Backend Server

Before running the server, make sure you are authorized in firsestore, otherwise commentout line no 38-51 agent-server/agent_utils.js

```bash
uvicorn main:app --reload
```

The backend server will be available at `http://localhost:8000`.

---

## Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will run at `http://localhost:3000`.

---

## Notes

- Make sure the backend server is running before starting the frontend.
- If needed, update the frontend's API base URL to match the backend server.

---