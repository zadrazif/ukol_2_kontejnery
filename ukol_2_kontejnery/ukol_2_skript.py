import json, pyproj, math, statistics
from pyproj import Transformer
from math import hypot 

def containers_file_open(container_file):
    try:
        with open(container_file, encoding = 'utf-8') as f:
            containers_input = json.load(f)
            features = containers_input['features']
    except ValueError:
        print(f"Soubor {container_file} je chybný.")
        exit()
    except FileNotFoundError:
        print(f"Soubor {container_file} nebyl nalezen.")
        exit()
    except PermissionError:
        print(f"Soubor {container_file} je nepřístupný.")
    
    return features

def container_access_filter(features):
    containers_coords_wgs = []
    for feature in features:
        if feature['properties']['PRISTUP'] == 'volně':
            souradnice = feature['geometry']['coordinates']
            containers_coords_wgs.append(souradnice)
    return containers_coords_wgs

def address_file_open(address_file):
    try:
        with open(address_file, encoding = 'utf-8') as f:
            address_input = json.load(f)
            addresses = address_input['features']
    except ValueError:
        print(f"Soubor {address_file} je chybný.")
        exit()
    except FileNotFoundError:
        print(f"Soubor {address_file} nebyl nalezen.")
        exit()
    except PermissionError:
        print(f"Soubor {address_file} je nepřístupný.")
    
    return addresses

def address_points(addresses):
    positions = []
    transformer = Transformer.from_crs(4326, 5514, always_xy=True)
    for adresa in addresses:
        records = {}
        records['adresa'] = adresa['properties']['addr:street'] + ' ' + adresa['properties']['addr:housenumber']
        records['souradnice'] = transformer.transform(adresa['geometry']['coordinates'][0], adresa['geometry']['coordinates'][1])
        positions.append(records)
    return positions

def containers_to_sjtsk(containers_coords_wgs):
    containers_coords_sjtsk = []
    transformer = Transformer.from_crs(4326, 5514, always_xy=True)
    for pt in transformer.itransform(containers_coords_wgs):
        containers_coords_sjtsk.append(pt)
    return containers_coords_sjtsk

def address_point_container_distance(positions, containers_coords_sjtsk):
    farthest_distance_address = 'David'
    distances = []
    farthest_value = 0
    for adresa in positions:
        shortest_distance = 10000
        for kontejner in containers_coords_sjtsk:
            diff_lon = adresa['souradnice'][0] - kontejner[0]
            diff_lat = adresa['souradnice'][1] - kontejner[1]
            distance = math.hypot(diff_lon, diff_lat)
            if distance <= shortest_distance:
                shortest_distance = distance
        distances.append(shortest_distance)
        if shortest_distance > farthest_value:
            farthest_value = shortest_distance
            farthest_distance_address = adresa['adresa']
    return farthest_value, farthest_distance_address, distances

features = containers_file_open("kontejnery.geojson")
addresses = address_file_open("adresy.geojson")  
containers_coords_wgs = container_access_filter(features) 
positions = address_points(addresses) 
containers_coords_sjtsk = containers_to_sjtsk(containers_coords_wgs)
farthest_value, farthest_distance_address, distances = address_point_container_distance(positions, containers_coords_sjtsk)
  
mean = statistics.mean(distances)
median = statistics.median(distances)

print("Celkem načteno", len(positions), "adresních bodů")
print("Celkem načteno", len(containers_coords_wgs), "kontejnerů na tříděný odpad")
print("Průměrná vzdálenost z adresního bodu ke kontejneru je:", f"{mean:.0f}", "m")
print("Medián vzdáleností z adresního bodu ke kontejneru je:", f"{median:.0f}", "m")
print("Největší vzdálenost ke kontejneru je", f"{farthest_value:.0f}", "m a to z adresy", farthest_distance_address)
