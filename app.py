from flask import Flask, render_template, request
import phonenumbers
from phonenumbers import carrier, geocoder
from opencage.geocoder import OpenCageGeocode
import folium
import os

app = Flask(__name__)

# It's better to use environment variables for API keys
OPENCAGE_KEY = os.getenv('OPENCAGE_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = request.form['phone_number']
        try:
            # Parse phone number
            parsed_num = phonenumbers.parse(number)
            
            # Get location and carrier
            location = geocoder.description_for_number(parsed_num, "en")
            service_pro = carrier.name_for_number(parsed_num, "en")
            
            # Geocode the location
            geocoder_api = OpenCageGeocode(OPENCAGE_KEY)
            results = geocoder_api.geocode(location)
            
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                
                # Create map
                mymap = folium.Map(location=[lat, lng], zoom_start=9)
                folium.Marker([lat, lng], popup=location).add_to(mymap)
                map_path = os.path.join('static', 'location.html')
                mymap.save(map_path)
                
                return render_template('template/index.html', 
                                     location=location,
                                     provider=service_pro,
                                     lat=lat,
                                     lng=lng,
                                     map_available=True)
            
        except Exception as e:
            return render_template('template/index.html', error=str(e))
    
    return render_template('template/index.html')

if __name__ == '__main__':
    app.run(debug=True)