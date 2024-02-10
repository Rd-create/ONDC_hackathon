from flask import Flask, request, jsonify
from flask_cors import CORS 
import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon
import geopy 
import logging

app = Flask(__name__)
CORS(app)  # Enabled CORS

@app.route('/create_polygon', methods=['POST'])
def create_polygon():
    data = request.json
    if not data or 'vertices' not in data or not data['vertices']:
        return jsonify({'error': 'Invalid input. Please provide non-empty vertices array.'}), 400

    vertices = data['vertices']
    pointlist = [Point(point) for point in vertices]

    # Create Shapely polygon
    try:
        polygon = Polygon(pointlist)
    except ValueError as e:
        app.logger.error(f"Invalid polygon vertices: {e}")  # Added logging
        return jsonify({'error': 'Invalid polygon vertices: ' + str(e)}), 400

    # Create GeoJSON representation
    polygon_geojson = gpd.GeoSeries([polygon]).to_json()

    # Visualize using Folium
    m = folium.Map(location=[polygon.centroid.y, polygon.centroid.x], zoom_start=12)
    folium.Polygon(locations=[(point.y, point.x) for point in pointlist],
                    color='blue', fill=True, fill_color='blue').add_to(m)

    # Ensure response is a dictionary with expected keys and valid JSON values
    response_data = {
        'message': 'Polygon created successfully',
        'polygon': polygon_geojson,
        'map_html': m.get_root().render()
    }

    # Log the response before returning
    app.logger.info(f"Returning response: {response_data}")

    return jsonify(response_data)  # Return dictionary as JSON

# Point format conversion function (unchanged)

if __name__ == '__main__':
    app.run(debug=True)
