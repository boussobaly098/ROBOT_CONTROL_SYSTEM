import math

from robot import Robot
from simulation import Simulation
from capteur import Capteur

simulation = Simulation()
simulation.obstacles = []
simulation.ajouter_obstacle("O_TEST", 110, 100, 10, 5)

robot = Robot(x=104.080964, y=102.831747, z=10)
capteur = Capteur()

destination = (150, 100, 10)

dx = destination[0] - robot.x
dy = destination[1] - robot.y
dz = destination[2] - robot.z

angle_voulu = math.degrees(math.atan2(dy, dx))
distance_h = math.sqrt(dx**2 + dy**2)
angle_vertical = math.degrees(math.atan2(dz, distance_h))

decalages = [0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90]

print("Position du robot :", robot.obtenir_position())
print("Angle souhaité :", angle_voulu)
print("\n--- TEST DES DIRECTIONS ---")

for decalage in decalages:
    angle = (angle_voulu + decalage) % 360

    a = math.radians(angle)
    v = math.radians(angle_vertical)

    pas = robot.vitesse

    nx = robot.x + pas * math.cos(v) * math.cos(a)
    ny = robot.y + pas * math.cos(v) * math.sin(a)
    nz = robot.z + pas * math.sin(v)

    collision = simulation.verifier_collision(robot, nx, ny, nz)

    robot.angle = angle
    robot.angle_vertical = angle_vertical

    distance_capteur = capteur.mesurer_distance(
        robot,
        simulation.obtenir_obstacles(),
        simulation.largeur,
        simulation.hauteur,
        simulation.profondeur
    )

    print(
        f"Direction {decalage:+4}° | "
        f"Collision : {collision} | "
        f"Distance capteur : {distance_capteur}"
    )