import json
import time
import requests
from kafka import KafkaProducer
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class WeatherProducer:
    def __init__(self, api_key, kafka_bootstrap_servers='kafka:9092'):
        self.api_key = api_key
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.topic = 'weather-data'
        
    def get_weather_data(self, city):
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data for {city}: {e}")
            return None
    
    def send_to_kafka(self, weather_data):
        """Gửi dữ liệu thời tiết vào Kafka topic"""
        if weather_data:
            weather_data['processed_at'] = datetime.now().isoformat()
            self.producer.send(self.topic, value=weather_data)
            self.producer.flush()
            print(f"✅ Sent weather data for {weather_data['name']} to Kafka")
    #dag
    def run_batch(self, cities, delay_between_cities=5):
        """Chạy 1 batch duy nhất"""
        for city in cities:
            weather_data = self.get_weather_data(city)
            if weather_data:
                self.send_to_kafka(weather_data)
            time.sleep(delay_between_cities)
        print("Batch finished ✅")
    