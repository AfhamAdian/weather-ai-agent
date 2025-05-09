from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

import requests
import json
import os
import getpass
from dotenv import load_dotenv
from datetime import datetime, date, time, timezone
import dateparser


load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")



model_helper = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ.get("GOOGLE_API_KEY")
)


# tokenize query input
def extractor_tokenizer(json_string):
    try:
        # Remove ```json and ``` from the beginning and end of the string
        cleaned_json = json_string.strip().lower()
        if cleaned_json.startswith("```json"):
            cleaned_json = cleaned_json[7:]  # Remove ```json
        if cleaned_json.endswith("```"):
            cleaned_json = cleaned_json[:-3]  # Remove ```
        
        # Strip any extra whitespace
        cleaned_json = cleaned_json.strip()
        # print(f"Cleaned JSON: {cleaned_json}")
        
        data = json.loads(cleaned_json)
        return data.get("city_name", "not_given"), data.get("date_or_time", "not_given"), data.get("weather_condition", "not_given")
    
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw JSON string: {json_string}")
        return {"error": "Invalid JSON format"}


# get lat-long from city name
def geocode_location(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "PostmanRusdfadntime/7.32.0" 
    }
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                "lat": data[0]["lat"],
                "lon": data[0]["lon"],
                "display_name": data[0]["display_name"]
            }
        else:
            return {"error": "No results found for the given city name."}
    else:
        return {"error": f"Request failed with status code {response.status_code}"}
        

    
# date_diff to select API call
def parse_date(date_str: str) -> str:
    """Parses a natural language date string into ISO format."""
    parsed = dateparser.parse(date_str)
    print(f"Parsed date: {parsed}")
    
    if parsed:
        return parsed.isoformat()
    return "Invalid date format."


def get_date_diff(date):
    tools = [
    Tool(
        name="DateParser",
        func=parse_date,
        description=f"Use this tool to convert natural language date phrases into a precise datetime. Today's date is {datetime.now().isoformat()}."
        )
    ]

    agent = initialize_agent(tools, model_helper, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
    result = agent.invoke(f"{date}. for your information, today is {datetime.now().isoformat()}. Always give both date and time with them seoarated bt T. For example, 2023-10-01T12:00:00. ")

    date_only = result['output'].split("T")[0]
    time_only = result['output'].split("T")[1]

    # Calculate the difference in days
    parsed_date = datetime.fromisoformat(date_only).date()
    today_date = datetime.today().date()
    date_diff = (parsed_date-today_date).days

    # Calculate the difference in hours
    current_time = datetime.now().time()
    parsed_time = datetime.fromisoformat(result['output']).time()

    # Combine parsed time with today's date
    today_given = datetime.combine(datetime.today().date(), parsed_time)
    now = datetime.now()

    # Calculate time difference
    time_difference = today_given - now
    time_diff = time_difference.total_seconds() / 3600

    return {
        "date_diff": date_diff,
        "time_diff": time_diff,
        "date_only": date_only,
        "time_only": time_only
    }


# get weather data from API
def get_weather_data(coord, results):
    # Extract variables from results
    date_diff = results["date_diff"]
    time_diff = results["time_diff"]
    date_only = results["date_only"]
    time_only = results["time_only"]
    lat = coord["lat"]
    lon = coord["lon"]

    url_seven_days = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely&appid={os.environ.get('OPENWEATHER_API_KEY')}"

    if date_diff == 0:
        print("API Call for current weather")
        if -1 < time_diff < 1:
            print("            Current hour weather")
            try:
                response = requests.get(url_seven_days)
                response.raise_for_status()
                data = response.json()
                cleaned_data = data["current"]

            except requests.exceptions.RequestException as e:
                print(f"Error fetching current weather data: {e}")


        else:
            print("            Current day, different hour weather")
            try:
                response = requests.get(url_seven_days)
                response.raise_for_status()
                data = response.json()
                cleaned_data = get_closest_hour_weather(data, time_only)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching current weather data: {e}")


    elif 0 < date_diff <= 7:
        print("API Call for future weather")
        try:
            response = requests.get(url_seven_days)
            response.raise_for_status()
            data = response.json()
            cleaned_data = get_closest_date_weather(data, date_only)


        except requests.exceptions.RequestException as e:
            print(f"Error fetching future weather data: {e}")


    elif -5 <= date_diff < 0:
        print("API Call for past weather")
        try:
            unix_time = convert_date_to_unix(date_only, fmt="%Y-%m-%d")
            
            url_past_five_days = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={unix_time}&appid={os.environ['OPENWEATHER_API_KEY']}"
        
            response = requests.get(url_past_five_days)
            response.raise_for_status()
            data = response.json()
            cleaned_data = data["data"]

        except ValueError as e:
            print(f"Error parsing date: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching past weather data: {e}")


    else:
        print("Cannot get weather data for more than 7 days in future or 5 days in past")
        return None

    return cleaned_data


# get closest Date Time helper
def convert_date_to_unix(date_str: str, fmt: str = "%Y-%m-%d") -> int:
    try:
        if fmt == "%H:%M:%S":
            # Handle time_only scenario by combining with today's date
            time_parts = date_str.split('.')
            clean_time = time_parts[0]  # Remove microseconds
            today = datetime.now().date()
            dt_with_time = datetime.combine(today, datetime.strptime(clean_time, fmt).time(), tzinfo=timezone.utc)
            return int(dt_with_time.timestamp())
        
        else:
            # Original code for date handling
            d = datetime.strptime(date_str, fmt).date()
            dt_utc_midnight = datetime.combine(d, time(0, 0, 0), tzinfo=timezone.utc)
            return int(dt_utc_midnight.timestamp())
    
    except ValueError as e:
        print(f"Error converting datetime: {e}, input: {date_str}, format: {fmt}")
        return int(datetime.now(timezone.utc).timestamp())


def get_closest_date_weather(data, date_only):
    daily_array = data["daily"]
    date_only = convert_date_to_unix(date_only, fmt="%Y-%m-%d")

    min_diff = float('inf')
    closest_day = None
    for day in daily_array:
        diff = abs(day["dt"] - date_only)
        if diff < min_diff:
            min_diff = diff
            closest_day = day
    if min_diff < 86400:
        return closest_day
    else:
        print("No close day found within 1 day range.")
        return None

def get_closest_hour_weather(data, time_only):
    hourly_array = data["hourly"]
    time_only = convert_date_to_unix(time_only, fmt="%H:%M:%S")
    print(f"Time only: {time_only}")

    min_diff = float('inf')
    closest_hour = None
    for hour in hourly_array:
        diff = abs(hour["dt"] - time_only)
        if diff < min_diff:
            min_diff = diff
            closest_hour = hour

    if min_diff < 3600:  
        return closest_hour
    else:
        print("No close hour found within 1 hour range.")
        return None
