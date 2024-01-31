import requests

def get_weather(city):
    api_url = f'http://api.openweathermap.org/data/2.5/find?q={city}'
    
    try:
        response = requests.get(api_url)
        data = response.json()

        if response.status_code == 200:
            if data['count'] > 0:
                temperature = data['list'][0]['main']['temp']
                description = data['list'][0]['weather'][0]['description']
                print(f'Weather in {city}: {temperature}°C, {description}')
            else:
                print(f'No weather data found for {city}')
        else:
            print(f'Unable to fetch weather data. Status Code: {response.status_code}')
    except Exception as e:
        print(f'Error during API request: {e}')

# Specify the city you're interested in
city_to_check = 'Bangkok'  # Replace with the city you're interested in

# Fetch and print weather information
get_weather(city_to_check)
