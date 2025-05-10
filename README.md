There is a FASTAPI server and a React frontend

Steps:
1. Clone the repo
2. Setup the agent-server
3. Setup the frontend
4. Run the agent server
5. Run the frontend


Explanation:

2. Setting up agent-server:
    Cd agent-server

    python -m venv venv
    source venv/bin/activate

    pip install -r agent-server/requirements.txt

    create a .env file in agent-server directory 
        GOOGLE_API_KEY=y3E
        OPENWEATHER_API_KEY=
        ELEVENLABS_API_KEY=
    paste these API-KEYs

    Then run the server with in port 8000 :
    uvicorn main:app --reload 



3. Setting up the frontend
    cd frontend

    npm install

    npm start