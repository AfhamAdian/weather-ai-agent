from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory

import os
import getpass
from dotenv import load_dotenv
import json
from datetime import datetime

from tools import extractor_tokenizer, geocode_location, get_date_diff, get_weather_data


load_dotenv()
verbosity = False


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")






#initializing firebase
PROJECT_ID = "weather-agent-80c59"
SESSION_ID = "01319014063"
COLLECTION_NAME = "chat_history"

print("Initializing Firebase...")
client = firestore.Client(project=PROJECT_ID)

print("Intializing Firebase chat history...")
chat_history = FirestoreChatMessageHistory(
    session_id = SESSION_ID,
    collection = COLLECTION_NAME,
    client = client
)

print("Firebase initialized successfully.")
print( chat_history.messages )

chat_history.add_message(SystemMessage(content="You are a weather agent"))  




# --- Model setup ---
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ.get("GOOGLE_API_KEY")
)

ligher_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.4,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ.get("GOOGLE_API_KEY")
)



# Extract Info from user query    
extractor_prompt_template = ChatPromptTemplate.from_template(
    "Extract the following information from the text:\n\n"
    "1. City name\n"
    "2. Date_or_time\n today, tomorrow, yesterday, saturday, sunday, monday etc. or two days from now, three days past today\n"
    "3. What type of weather condition user concerned about\n\n"
    "User query: {text}\n\n"
    "Query can be in any language. Translate to English and standardize it.\n\n"
    "response in JSON format:insert not_given in the corresponding field if you cannot find the information\n"
    "{{\n"
    "  \"city_name\": \"\",\n"
    "  \"date_or_time\": \"\",\n"
    "  \"weather_condition\": \"\"\n"
    "}}"
)

def extract_info(text: str) -> str:
    msgs = extractor_prompt_template.format_prompt(text=text).to_messages()
    raw = ligher_model(msgs)
    return StrOutputParser().parse(raw)

extractor_tool = Tool(
    name="InfoExtractor",
    func=extract_info,
    description="Extracts city_name, date_or_time, and weather_condition as JSON; uses 'not_given' if unclear. Just give me the JSON response with city, date and weather_condition. Do not give me the city name. I dont need any other details",
)

extractor_agent = initialize_agent(
    tools=[extractor_tool],
    llm=model,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=verbosity
)
    
chainExtractInfoFromQuery = (
    RunnableLambda(
        lambda x: extractor_agent.invoke(x["text"])
    )
    | RunnableLambda(
        lambda x: x.get("output", str(x))
    )
    | StrOutputParser()
    | RunnableLambda(
        lambda x: extractor_tokenizer(x)
    )
)




# Respond to the user query given the weather data
response_template = ChatPromptTemplate.from_template(
    "You are a weather agent. You have to respond to the user query based on the weather data you have.\n\n"
    "It is certain that the weather data is correct and of that particular date or time.\n\n"
    "User query: {user_query}\n\n"
    "Weather data: {weather_data}\n\n"
    "Respond in this manner:\n"
    "{{ response : your response}}\n\n"
    "Also make sure to detect user sentiment and respond accordingly.\n\n"
    "MUST Respond only JSON Format"
)

chainRespondToUser = (
    response_template
    | model
    | StrOutputParser()
)




def clean_response(response):
    # Remove leading whitespace and ```json if present
    if response.lstrip().startswith("```json"):
        response = response[response.find("```json") + 7:]
    elif response.lstrip().startswith("```"):
        response = response[response.find("```") + 3:]
    
    # Remove trailing whitespace and ``` if present
    if response.rstrip().endswith("```"):
        response = response[:response.rfind("```")]
        
    return response.strip()




def ans_to_user_query( query ):
    city, date, weather_condition = chainExtractInfoFromQuery.invoke({
        "text": query
    })
    print("City: ", city, " Date: ", date, " Weather_Condition: ", weather_condition)

    coord = geocode_location(city)
    result = get_date_diff(date)
    response = get_weather_data(coord, result)

    # Respond to the user query given the weather data
    response = chainRespondToUser.invoke({
        "user_query": query,
        "weather_data": response
    })

    print("Response:", response)
    response = response.strip()

    clean_response_var = clean_response(response)
    print("Cleaned Response: ", clean_response_var)

    response_json = json.loads(clean_response_var)
    print("Response JSON: ", response_json)
    return response_json



# ans_to_user_query("will it rain catsand dogs in dhaka a hour from now?")




# print("Welcome to the Weather Agent. Type 'exit' to quit.")
# while True:
#     query = input("Enter your query: ")
#     if query.lower() == "exit":
#         break
    
#     print("Processing your query...")
#     msgs = chat_history.messages
#     print("Chat history: ", msgs)

#     chat_history.add_user_message(query)
#     ans_to_user_query(query)
