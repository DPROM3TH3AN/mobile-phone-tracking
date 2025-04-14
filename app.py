# Add monkey patch at the top
import collections
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

from flask import Flask, render_template, request
import phonenumbers
from phonenumbers import carrier, geocoder
from opencage.geocoder import OpenCageGeocode
import folium
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')
OPENCAGE_KEY = os.getenv('OPENCAGE_KEY')

if not OPENCAGE_KEY:
    raise ValueError("OPENCAGE_KEY environment variable is missing!")

if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = request.form['phone_number']
        try:
            parsed_num = phonenumbers.parse(number)
            location = geocoder.description_for_number(parsed_num, "en")
            service_pro = carrier.name_for_number(parsed_num, "en")
            
            geocoder_api = OpenCageGeocode(OPENCAGE_KEY)
            results = geocoder_api.geocode(location)
            
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                
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
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)