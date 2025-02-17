from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.place import Place
from models.state import State
from models.city import City

def get_places_by_states(states):
    """Retrieve all Place objects related to a list of State IDs."""
    places = []
    for state_id in states:
        state = storage.get(State, state_id)
        if state:
            for city in state.cities:
                places.extend(city.places)
    return places

def get_places_by_cities(cities):
    """Retrieve all Place objects related to a list of City IDs."""
    places = []
    for city_id in cities:
        city = storage.get(City, city_id)
        if city:
            places.extend(city.places)
    return places

def filter_places_by_amenities(places, amenities):
    """Filter places to include only those having all specified amenities."""
    filtered_places = []
    for place in places:
        place_amenity_ids = {amenity.id for amenity in place.amenities}
        if all(amenity_id in place_amenity_ids for amenity_id in amenities):
            filtered_places.append(place)
    return filtered_places

@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def search_places():
    """Search for Place objects based on JSON request body."""
    body = request.get_json(silent=True)
    if body is None:
        abort(400, "Not a JSON")
    
    states = body.get("states", [])
    cities = body.get("cities", [])
    amenities = body.get("amenities", [])
    
    if not states and not cities:
        places = list(storage.all(Place).values())
    else:
        places = get_places_by_states(states) + get_places_by_cities(cities)
    
    if amenities:
        places = filter_places_by_amenities(places, amenities)
    
    return jsonify([place.to_json() for place in places])
