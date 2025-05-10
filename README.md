There is a FASTAPI server with a React frontend.

Steps:
1. Clone the repo
2. Setup the agent-server
3. Setup the frontend
4. Run the agent server
5. Run the frontend


Explanation:

A. Setting up agent-server
steps :
    Cd agent-server

    python3 -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt

    create a .env file in agent-server directory 
        GOOGLE_API_KEY=y3E
        OPENWEATHER_API_KEY=
        ELEVENLABS_API_KEY=
    paste these API-KEYs

    Then run the server with in port 8000 :
    uvicorn main:app --reload 



B. Setting up the frontend 
steps :
    cd frontend

    npm install

    npm start