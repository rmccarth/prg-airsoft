import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)

#this is a function that would change based on users supplying where they would want to fly the drone
#for now we will caluclate where the square coordinates are based on drone starting here:
#     -------
#     |     |
#     |     |
#     ---x---

def calculate_square(lat, long, width):
    # initialize our coordinate pairs
    bottom_left = []
    top_left = []
    top_right = []
    bottom_right = []

    bottom_left_lat = lat - width / 2
    bottom_left_long = long
    bottom_left.append(bottom_left_lat)
    bottom_left.append(long)

    top_left_lat = bottom_left_lat
    top_left_long = bottom_left_long + width
    top_left.append(top_left_lat)
    top_left.append(top_left_long)

    top_right_lat = top_left_lat + width
    top_right_long = top_left_long
    top_right.append(top_right_lat)
    top_right.append(top_right_long)

    bottom_right_lat = top_right_lat
    bottom_right_long = top_right_long - width
    bottom_right.append(bottom_right_lat)
    bottom_right.append(bottom_right_long)


    coordinates = {}
    coordinates["bottom_left"] = bottom_left
    coordinates["top_left"] = top_left
    coordinates["top_right"] = top_right
    coordinates["bottom_right"] = bottom_right

    return coordinates

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered with UUID: {}".format(state.uuid))
            break

    location = drone.telemetry.position()
    
    async for position in location:
        init_latitude = position.latitude_deg
        init_longitude = position.longitude_deg
        break
    
    print("-- Arming")
    await drone.action.arm()


    square_coordinates = calculate_square(init_latitude, init_longitude, .0001)

    mission_items = []
    mission_items.append(MissionItem(init_latitude, init_longitude, 100, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan')))
    for key in square_coordinates.keys():
        latitude = square_coordinates[key][0]
        longitude = square_coordinates[key][1]
        mission_items.append(MissionItem(latitude, longitude, 100, 5, False, float('nan'), float('nan'), MissionItem.CameraAction.TAKE_PHOTO, float('nan'), float('nan')))

    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    await drone.mission.start_mission()

    return init_latitude, init_longitude, drone

async def land():

    print("-- RTB")
    await drone.action.return_to_launch()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    init_latitude, init_longitude, drone = loop.run_until_complete(run())
    