import requests
from collections import Counter
from geopy.distance import geodesic
import numpy as np

def calculate_distance(start_lat, start_lon, end_lat, end_lon):
    """Calculate the distance between two latitude/longitude points."""
    start_point = (start_lat, start_lon)
    end_point = (end_lat, end_lon)
    return geodesic(start_point, end_point).km

def generate_intermediate_points(start_lat, start_lon, end_lat, end_lon, num_points):
    """Generate evenly spaced intermediate points between start and end points."""
    lats = np.linspace(start_lat, end_lat, num_points + 2)  # Including start and end
    lons = np.linspace(start_lon, end_lon, num_points + 2)  # Including start and end
    return list(zip(lats[1:-1], lons[1:-1]))  # Exclude start and end points

def fetch_terrain(lat, lon):
    """Fetch land use data from OpenStreetMap."""
    try:
        radius = 500  # Radius in meters for precision
        url = f"https://overpass-api.de/api/interpreter?data=[out:json][timeout:25];(node(around:{radius},{lat},{lon});way(around:{radius},{lat},{lon});relation(around:{radius},{lat},{lon}););out body;>;out skel qt;"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        land_use_types = set()
        for element in data.get('elements', []):
            if 'tags' in element:
                tags = element['tags']
                land_use = tags.get('landuse') or tags.get('natural')
                if land_use:
                    land_use_types.add(land_use)

        # Map land use types to categories
        categorized_terrain = categorize_terrain(land_use_types)

        if categorized_terrain:
            return ', '.join(categorized_terrain)
        return 'Unknown'
    except requests.RequestException as e:
        print(f"HTTP Request error: {e}")
        return 'Error: HTTP Request failed'
    except ValueError as e:
        print(f"JSON Parsing error: {e}")
        return 'Error: JSON Parsing failed'
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 'Error: Unexpected error'

def categorize_terrain(land_use_types):
    """Categorize terrain based on land use types."""
    terrain_categories = {
        'forest': {'forest', 'wood', 'scrub'},
        'water': {'water'},
        'flatlands': {'meadow', 'grass'},
        'urban': {'retail', 'commercial', 'industrial', 'brownfield'},
        'transport': {'railway'},
        'recreational': {'recreation_ground'},
        'agricultural': {'farmyard', 'farmland', 'orchard'},
        'military': {'military'},
        'cemetery': {'cemetery'},
        'unknown': {'Unknown'}
    }

    categorized_terrain = set()
    for category, types in terrain_categories.items():
        if land_use_types & types:
            categorized_terrain.add(category)
    
    return categorized_terrain

def count_terrain_categories(terrain_info):
    """Count occurrences of each terrain category in the list of terrain info."""
    terrain_counts = Counter()
    for terrain in terrain_info:
        for category in terrain.split(', '):
            terrain_counts[category] += 1

    # Convert terrain counts to a list of dictionaries
    return [{"terrain": terrain, "count": count} for terrain, count in terrain_counts.items()]
