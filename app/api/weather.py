import requests
import json
from datetime import datetime, timedelta

# Load API key from JSON file
with open('weather_api.json', 'r') as file:
    api_key = json.load(file)['api_key']
print(f"API Key: {api_key}")

# Revised cost matrix with refined values
cost_matrix = {
    "car": {"rain": 7, "clouds": 6, "clear": 5, "fog": 9},
    "boat": {"rain": 8, "clouds": 7, "clear": 6, "fog": 12},
    "helicopter": {"rain": 14, "clouds": 8, "clear": 4, "fog": 11},
    "foot": {"rain": 9, "clouds": 7, "clear": 5, "fog": 14}
}

# Strategy and objective cost modifiers with more impact for adjustments
strategy_modifier = {
    "aggressive": {"defensive": 2, "capture/extract HVT": 5, "infiltrate target": 6},
    "stealth": {"defensive": 6, "capture/extract HVT": 4, "infiltrate target": 2}
}

def fetch_weather(api_key, lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching weather data: {response.status_code}")
        return {'time_windows': []}

    weather_data = response.json()

    time_windows = []
    for entry in weather_data['list']:
        date_time = entry['dt_txt']
        weather_main = entry['weather'][0]['main'].lower()
        if weather_main in ['rain', 'clouds', 'clear', 'fog']:
            time_windows.append({
                'interval': date_time,
                'weather': weather_main
            })
    
    return {'time_windows': time_windows}

def evaluate_cost(vehicle, weather_conditions, strategy, objective):
    base_costs = [cost_matrix[vehicle].get(weather, float('inf')) for weather in weather_conditions]
    avg_base_cost = sum(base_costs) / len(base_costs)

    strategy_cost = strategy_modifier[strategy].get(objective, 0)

    # Additional adjustments for weather and strategy
    if strategy == "stealth":
        if "rain" in weather_conditions:
            avg_base_cost *= 0.85  # More significant benefit from rain for stealth
        if "clouds" in weather_conditions:
            avg_base_cost *= 0.90  # Slight benefit from clouds for stealth
        if "clear" in weather_conditions:
            avg_base_cost *= 1.2  # Clear conditions are more costly for stealth

    elif strategy == "aggressive":
        if "rain" in weather_conditions:
            avg_base_cost *= 1.15  # Increased cost due to rain challenges for aggressive strategy
        if "clouds" in weather_conditions:
            avg_base_cost *= 1.1  # Slightly higher cost due to reduced visibility from clouds

    print(f"Weather Conditions: {weather_conditions}")
    print(f"Base Costs: {base_costs}, Average Base Cost: {avg_base_cost}, Strategy Cost: {strategy_cost}")
    
    return avg_base_cost + strategy_cost

def find_best_time_window(api_key, lat, lon, start_date, end_date, duration_hours, vehicle, strategy, objective):
    weather_data = fetch_weather(api_key, lat, lon)
    
    if not weather_data['time_windows']:
        print("No weather data available.")
        return None, float('inf'), None
    
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    duration = timedelta(hours=duration_hours)
    window_duration = timedelta(hours=3)  # Each window represents a 3-hour forecast

    best_cost = float('inf')
    best_time_window = None
    best_weather_conditions = None

    for i in range(len(weather_data['time_windows'])):
        start_time = datetime.strptime(weather_data['time_windows'][i]['interval'], '%Y-%m-%d %H:%M:%S')

        if start_time >= start_datetime and start_time <= end_datetime:
            end_time = start_time + duration
            
            if end_time <= end_datetime:
                total_cost = 0
                weather_conditions = []
                valid = True
                current_time = start_time

                while current_time < end_time:
                    found_window = False
                    for time_window in weather_data['time_windows']:
                        window_time = datetime.strptime(time_window['interval'], '%Y-%m-%d %H:%M:%S')
                        if window_time == current_time:
                            current_weather = time_window['weather']
                            weather_conditions.append(current_weather)
                            found_window = True
                            break
                    if not found_window:
                        valid = False
                        break
                    current_time += window_duration

                if valid:
                    avg_cost = evaluate_cost(vehicle, weather_conditions, strategy, objective)
                    
                    if avg_cost < best_cost:
                        best_cost = avg_cost
                        best_time_window = start_time.strftime('%Y-%m-%d %H:%M:%S')
                        best_weather_conditions = weather_conditions
                        print(f"New best window found: Start Time = {best_time_window}, Cost = {best_cost}, Conditions = {best_weather_conditions}")

    if best_time_window is None:
        if weather_data['time_windows']:
            best_time_window = weather_data['time_windows'][0]['interval']
            best_weather_conditions = [weather_data['time_windows'][0]['weather']]
            best_cost = float('inf')
            print("No suitable time window found for the given duration. Using fallback window.")

    return best_time_window, best_cost, best_weather_conditions

# Example usage
lat = 40.712776  # Example latitude (New York City)
lon = -74.005974  # Example longitude (New York City)
start_date = '2024-09-15'
end_date = '2024-09-20'
duration_hours = 6  # Duration of the mission
vehicle = 'helicopter'
strategy = 'stealth'
objective = 'defensive'

best_time_window, best_cost, best_weather_conditions = find_best_time_window(api_key, lat, lon, start_date, end_date, duration_hours, vehicle, strategy, objective)
print(f"Best Time Window: {best_time_window}")
print(f"Weather Conditions: {best_weather_conditions}")
print(f"Best Cost: {best_cost}")

if best_time_window:
    print(f"Reason: The best time window was selected based on the lowest average cost for the given vehicle, strategy, and objective within the specified duration. The weather conditions during this time were {best_weather_conditions}, which influenced the overall cost evaluation.")
else:
    print("No suitable time window was found.")
