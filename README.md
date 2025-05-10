# Weather-AI-Agent :
 AI agent for you weather queries.

![Sample Image](https://media-hosting.imagekit.io/c442d061ca09431a/f40ea915-5596-4ce6-855e-332dcdf08d5d.jpeg?Expires=1841508272&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=lynYPomo-d1YBupABzmK1pbUDqOsRwGHnRRwXmsAq~bnGOZco7G4k4PujZj-8iDS0JOVIO39pln1JtjbAuUWIaq84gc17V2qlEF~SbE9Uytib5v2~6-B28UUivW9zny9QOMk3zMxwHUJ4YAmvydneKcUf7TQ2Ljb4gt1een3XcHkDgpEgE0MLrTNnO6GBPQthCcNKCg7MUPxp8S35oLsGSvSAGZxYZYSy9ZwoRy4vNq27JhXcSAyIwbOyXHupbf7CtrKGiZszmza3Ql4l53psI3AsLtN4lRhwTJqxSTtoMbs0sw2nbva9DwNeKlo6ufS7cFyHMuSAF03rIvtxNxQbA__)


---

## Getting Started
This project is built with fastAPI server and a REACT frontend. Gemini 2.0 flash and elevelabs funcionalities are used as AI components.
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
