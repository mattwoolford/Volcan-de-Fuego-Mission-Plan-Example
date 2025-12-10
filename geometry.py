import geopandas as gp
import numpy as np
from numpy.ma.core import tan
from shapely.geometry import Point

from settings import SETTINGS


def calculate_climb_h_distance(target_pitch_degs: float, target_altitude: float):
    return abs(target_altitude / tan(np.deg2rad(target_pitch_degs)))


def calculate_euclidean_distance(origin: tuple | int | float, destination: tuple | int | float):
    return np.linalg.norm(np.array(origin) - np.array(destination))


def add_polar_waypoints(origin: tuple[float, float, int], target: tuple[float, float, int]):

    # Set the start and target coordinates
    start = origin

    # Find the altitude difference between the start and target
    altitude_change = max(target[2], start[2]) - min(target[2], start[2])

    # Get the horizontal distance required for the climb out
    climb_h_distance_in_m = calculate_climb_h_distance(target_pitch_degs=SETTINGS["MISSION"]["TARGET_CLIMB_DEG"],
                                                       target_altitude=altitude_change)

    # Get the horizontal distance required for the descent back in
    descent_h_distance_in_m = calculate_climb_h_distance(target_pitch_degs=SETTINGS["MISSION"]["TARGET_DESCENT_DEG"],
                                                         target_altitude=altitude_change)

    # Get the distance between the start and the target by geographical projection
    geo_data_points = gp.GeoSeries([Point(start[1], start[0]), Point(target[1], target[0])], crs="EPSG:4326")
    geo_data_points_projection = geo_data_points.to_crs(geo_data_points.estimate_utm_crs())
    start_point_in_m, target_point_in_m = geo_data_points_projection[0], geo_data_points_projection[1]
    # offset distance from the crater would = `start_point_in_m.distance(target_point_in_m)`

    # Find the gradients between the start and end point (change in "x" / change in "y")
    dx = target_point_in_m.x - start_point_in_m.x
    dy = target_point_in_m.y - start_point_in_m.y

    # Calculate waypoints either side of the volcano (two right-angled triangles by adding / subtracting the change in "x" and "y", respectively)
    waypoint1 = Point(start_point_in_m.x + dx / 2, start_point_in_m.y + dy / 2 + dx)
    waypoint2 = Point(start_point_in_m.x + dx / 2 + dy,
                      start_point_in_m.y + dy / 2 - dx)

    # Collect waypoints
    waypoints = [start_point_in_m, waypoint1, target_point_in_m, waypoint2]

    # Convert projection back into decimal degrees (geographical coordinates)
    coor_points = gp.GeoSeries(waypoints,
                               crs=geo_data_points_projection.crs).to_crs("EPSG:4326")

    # Return coordinate values
    return [(point.y, point.x) for point in coor_points]
