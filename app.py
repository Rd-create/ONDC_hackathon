from flask import Flask, request, jsonify
import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon
import geopy  # For point format conversion

app = Flask(__name__)

@app.route('/create_polygon', methods=['POST'])
def create_polygon():
    data = request.json
    if not data or 'vertices' not in data or not data['vertices']:
        return jsonify({'error': 'Invalid input. Please provide non-empty vertices array.'}), 400

    vertices = data.get('vertices')
    # point_format = data.get('point_format', 'gps')  # Default to GPS

    # Convert vertices to Shapely points based on specified format
    # try:
    #     points = [convert_point_format(vertex, point_format) for vertex in vertices]
    # except ValueError as e:
    #     return jsonify({'error': str(e)}), 400

    # Create Shapely polygon
    points = vertices
    try:
        polygon = Polygon(points)
    except ValueError as e:
        return jsonify({'error': 'Invalid polygon vertices: ' + str(e)}), 400

    # Create GeoJSON representation
    polygon_geojson = gpd.GeoSeries([polygon]).to_json()

    # Visualize using Folium
    m = folium.Map(location=[polygon.centroid.y, polygon.centroid.x], zoom_start=12)
    folium.Polygon(locations=[(point.y, point.x) for point in points],
                    color='blue', fill=True, fill_color='blue').add_to(m)

    map_html_path = 'map.html'
    m.save(map_html_path)

    return jsonify({'message': 'Polygon created successfully'})


# Point format conversion function
def convert_point_format(point, format):
    format_lower = format.lower()  # Convert format to lowercase
    if format_lower == "gps":
        return Point(geopy.Point(point).longitude, geopy.Point(point).latitude)
    elif format_lower == "s2":
        return Point(geopy.Point.from_s2_cellid(point).longitude, geopy.Point.from_s2_cellid(point).latitude)
    elif format_lower == "h3":
        return Point(geopy.Point.from_h3_index(point).longitude, geopy.Point.from_h3_index(point).latitude)
    else:
        raise ValueError("Unsupported point format")

if __name__ == '__main__':
    app.run(debug=True)
