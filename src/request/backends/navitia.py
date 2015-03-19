# Key for the apim when it asks user enter the key, passwd empty
api_key = '8f27fa71-4470-435e-b207-1cf5dd1aed85'

# Request to get the coord of the point you want to go to: https://api.navitia.io/v1/coverage/fr-idf/places?q=glaciere 

# for a metro station, check that it is a stop_area, how to distinguish between metro stations and bus stations that have the same name?
glaciere_coord = {"embedded_type": "stop_area", "stop_area": {"comment": "", "name": "Glaci\u00e8re", "links": [], "coord": {"lat": "48.830861", "lon": "2.344552"}, "label": "Glaci\u00e8re (Paris)", "administrative_regions": [{"insee": "75056", "name": "Paris", "level": 8, "coord": {"lat": "48.856506", "lon": "2.352133"}, "label": "Paris", "id": "admin:7444", "zip_code": ""}], "timezone": "Europe/Paris", "id": "stop_area:RTP:SA:1962"}, "quality": 90, "id": "stop_area:RTP:SA:1962", "name": "Glaci\u00e8re (Paris)"}

# for a street name, ensure that the name of the administrative_regions is Paris: don't get the rue riquet in aulnay sous bois...
rue_riquet_coord = {"embedded_type": "address", "address": {"name": "Rue Riquet", "house_number": 0, "coord": {"lat": "48.88951428156718", "lon": "2.3682064143445656"}, "label": "Rue Riquet (Paris)", "administrative_regions": [{"insee": "75056", "name": "Paris", "level": 8, "coord": {"lat": "48.856506", "lon": "2.352133"}, "label": "Paris", "id": "admin:7444", "zip_code": ""}], "id": "2.3682064143445656;48.88951428156718"}, "quality": 80, "id": "2.3682064143445656;48.88951428156718", "name": "Rue Riquet (Paris)"}



# itineraire from glaciere to rue riquet: http://api.navitia.io/v1/journeys?from=stop_area:RTP:SA:1962&to=2.3682064143445656;48.88951428156718 
# can add &commercial_mode=metro to obtain only metro itineraries

# Correct URL:
# http://api.navitia.io/v1/journeys?from=stop_area:RTP:SA:1962&to=2.3682064143445656;48.88951428156718&commercial_mode=metro&datetime=20150319T233000&datetime_represents=arrival 
# from and to take ids 
# get ids with the following URLs:
# http://api.navitia.io/v1/coverage/fr-idf/places?q=glaciere and filter the metro station (not really clear how to do so)
# and http://api.navitia.io/v1/coverage/fr-idf/places?q=glaciere filter the correct location (correct city)
