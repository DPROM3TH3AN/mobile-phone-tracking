# Add monkey patch at the top for compatibility with Python 3.10+ 
import collections
import collections.abc
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'MutableSequence'):
    collections.MutableSequence = collections.abc.MutableSequence

from flask import Flask, render_template, request
import phonenumbers
from phonenumbers import carrier, geocoder
from opencage.geocoder import OpenCageGeocode
import folium
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='templates')
OPENCAGE_KEY = os.getenv('OPENCAGE_KEY')

if not OPENCAGE_KEY:
    raise ValueError("OPENCAGE_KEY environment variable is missing!")

# Ensure the static folder exists for saving generated maps
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = request.form['phone_number']
        try:
            # Parse the phone number
            parsed_num = phonenumbers.parse(number)
            location = geocoder.description_for_number(parsed_num, "en")
            service_pro = carrier.name_for_number(parsed_num, "en")
            
            # Use the OpenCage API to retrieve geographic details
            geocoder_api = OpenCageGeocode(OPENCAGE_KEY)
            results = geocoder_api.geocode(location)
            
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                
                # Generate map using folium
                mymap = folium.Map(location=[lat, lng], zoom_start=9)
                folium.Marker([lat, lng], popup=location).add_to(mymap)
                map_path = os.path.join('static', 'location.html')
                mymap.save(map_path)
                
                return render_template('index.html', 
                                       location=location,
                                       provider=service_pro,
                                       lat=lat,
                                       lng=lng,
                                       map_available=True)
            
        except Exception as e:
            # Render errors gracefully in the UI
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
