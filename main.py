import requests
import time
import pandas as pd


def get_city_coordinates(api_key, city_name):
    """
    Retrieves the latitude and longitude of a city using the Google Geocoding API.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": api_key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print("City not found.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def search_places(api_key, location, keyword, radius=10000):
    """
    Searches for places using the Google Places API (Nearby Search), including paginated results.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{location[0]},{location[1]}",
        "radius": radius,
        "keyword": keyword,
    }
    results = []

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results.extend([
                {"name": place["name"], "place_id": place["place_id"]}
                for place in data.get("results", [])
            ])

            # Check for next_page_token
            next_page_token = data.get("next_page_token")
            if next_page_token:
                time.sleep(2)  # Wait for token activation
                params["pagetoken"] = next_page_token
            else:
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return results


def get_place_details(api_key, place_id):
    """
    Retrieves detailed information about a place using the Google Place Details API.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "key": api_key,
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,rating,user_ratings_total,website"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get("result", {})
        return {
            "name": data.get("name"),
            "address": data.get("formatted_address"),
            "phone": data.get("formatted_phone_number"),
            "rating": data.get("rating"),
            "review_count": data.get("user_ratings_total"),
            "website": data.get("website"),
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return {}


def save_to_excel(data, filename):
    """
    Saves the extracted place details to an Excel file.
    """
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    # Replace with your actual Google API key
    API_KEY = "API-KEY"

    # User input for search
    keyword = input("Enter a keyword (e.g., HVAC services): ")
    city_name = input("Enter a city name (e.g., Miami): ")

    # Step 1: Get city coordinates
    coordinates = get_city_coordinates(API_KEY, city_name)
    if coordinates:
        print(f"Coordinates of {city_name}: {coordinates}")

        # Step 2: Search for places
        places = search_places(API_KEY, coordinates, keyword)
        print(f"Found {len(places)} places for '{keyword}' in {city_name}.")

        # Step 3: Get details for each place
        detailed_places = []
        for place in places:
            details = get_place_details(API_KEY, place["place_id"])
            if details:
                detailed_places.append(details)

        # Step 4: Save results to Excel
        if detailed_places:
            filename = f"{city_name}_{keyword.replace(' ', '_')}_places.xlsx"
            save_to_excel(detailed_places, filename)
        else:
            print("No detailed place data to save.")
    else:
        print("Failed to retrieve city coordinates.")
