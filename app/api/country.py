from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_country_from_coords(latitude, longitude):
    geolocator = Nominatim(user_agent="anaygandhi")
    location = None
    
    try:
        location = geolocator.reverse((latitude, longitude), language='en')
    except GeocoderTimedOut:
        return "Geocoding service timed out. Please try again later."
    
    if location and location.raw.get('address'):
        address = location.raw['address']
        return address.get('country', 'Country not found')
    else:
        return "Location not found"
