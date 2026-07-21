import os
import random
from dotenv import load_dotenv
load_dotenv()


class AirlineService:
    def get_flights(self, params):
        origin = params['origin']
        destination = params['destination']
        outbound_date = params['outbound_date']

        airlines = ["Delta Air Lines", "United Airlines", "American Airlines", "British Airways", "Air Canada", "Lufthansa","United Arab Emirates"]
        airplanes = ["Boeing 787 Dreamliner", "Airbus A320", "Boeing 777", "Airbus A350"]
        
        flights = []
        for i in range(random.randint(2, 4)):
            airline = random.choice(airlines)
            flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
            duration = random.randint(120, 720) # 2 to 12 hours
            
            # Format outbound_date to ensure it's a string if it's a date object
            date_str = outbound_date.strftime("%Y-%m-%d") if hasattr(outbound_date, "strftime") else str(outbound_date)
            
            flights.append({
                "id": 1000 + i,
                "origin": origin,
                "destination": destination,
                "outbound_date": date_str,
                "return_date": None,
                "airline": airline,
                "flight_number": flight_number,
                "departure_time": f"{random.randint(6, 22):02d}:{random.choice([0, 15, 30, 45]):02d}",
                "arrival_time": f"{random.randint(6, 22):02d}:{random.choice([0, 15, 30, 45]):02d}",
                "duration_minutes": duration,
                "stops": random.choice([0, 1]),
                "price": float(random.randint(250, 1200)),
                "airplane": random.choice(airplanes)
            })

        return {
            "best_flights": flights,
            "other_flights": []
        }