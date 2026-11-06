from robot import Robot
from simulation import Simulation
from capteur import Capteur

# Création des objets
robot = Robot(x=100, y=200, z=10)
simulation = Simulation()
capteur = Capteur()

# Mesure de la distance
distance = capteur.mesurer_distance(
    robot,
    simulation.obtenir_obstacles(),
    simulation.largeur,
    simulation.hauteur,
    simulation.profondeur
)

# Détection
etat = capteur.detecter_obstacle(distance)

print("Position du robot :", robot.obtenir_position())
print("Distance détectée :", distance)
print("État du capteur :", etat)