from flask import Flask, request, jsonify, render_template
import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon
import geopy  # For point format conversion

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/creating_polygon')
def creating_polygon():
    return render_template('creating_polygon.html')

@app.route('/create_polygon', methods=['POST'])
def create_polygon():
    data = request.json
    if not data or 'vertices' not in data or not data['vertices']:
        return jsonify({'error': 'Invalid input. Please provide non-empty vertices array.'}), 400

    vertices = data.get('vertices')
    point_format = data.get('point_format', 'gps')  # Default to GPS

    # Convert vertices to Shapely points based on specified format
    try:
        points = [convert_point_format(vertex, point_format) for vertex in vertices]
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Create Shapely polygon
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

    return jsonify({'message': 'Polygon created successfully', 'polygon': polygon_geojson, 'map_html': m.get_root().render()})


# Point format conversion function
def convert_point_format(point, format):
    if format == "gps":
        return Point(geopy.Point(point).longitude, geopy.Point(point).latitude)
    elif format == "s2":
        return Point(geopy.Point.from_s2_cellid(point).longitude, geopy.Point.from_s2_cellid(point).latitude)
    elif format == "h3":
        return Point(geopy.Point.from_h3_index(point).longitude, geopy.Point.from_h3_index(point).latitude)
    else:
        raise ValueError("Unsupported point format")

if __name__ == '__main__':
    app.run(debug=True)
