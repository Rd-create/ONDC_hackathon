from flask import Flask, request, jsonify
import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon
import geopy  # For point format conversion

app = Flask(__name__)

@app.route('/create_polygon', methods=['POST'])
def create_polygon():
    data = request.json
    vertices = data.get('vertices')
    point_format = data.get('point_format', 'gps')  # Default to GPS

    # Convert vertices to Shapely points based on specified format
    points = [convert_point_format(vertex, point_format) for vertex in vertices]

    # Create Shapely polygon
    polygon = Polygon(points)

    # Create GeoJSON representation
    polygon_geojson = gpd.GeoSeries([polygon]).to_json()

    # Visualize using Folium (optional)
    m = folium.Map(location=polygon.centroid.coords, zoom_start=12)
    folium.Polygon(locations=[point.coords for point in points],
                    color='blue', fill=True, fill_color='blue').add_to(m)
    m.save('map.html')  # Optional save

    return jsonify({'message': 'Polygon created successfully', 'polygon': polygon_geojson})

# Point format conversion function (same as before)
def convert_point_format(point, format):
    # ... (implementation from previous response)

if __name__ == '__main__':
    app.run(debug=True)
