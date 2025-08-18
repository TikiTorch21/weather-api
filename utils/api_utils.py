import requests

def get_weather_from_city(city, api_key, metric):
    """
    Get weather data from openweathermap.org given a city name and API key.
    
    Parameters
    ----------
    city : str
        The name of the city to get the weather for.
    api_key : str
        The API key to use.
    metric : str
        The unit of measurement to return the weather in.
        May be "metric" or "imperial".
    
    Returns
    -------
    main : dict
        A dictionary containing the weather data.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={metric}"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data['main']