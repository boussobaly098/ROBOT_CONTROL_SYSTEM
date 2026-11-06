from robot import Robot
from obstacle import Obstacle
from simulation import Simulation
from capteur import Capteur
from automatique import Automatique

# Création des composants
robot = Robot(x=100, y=200, z=10)
simulation = Simulation()
capteur = Capteur()

automatique = Automatique(robot, capteur, simulation)

# Définition de la destination
automatique.definir_destination(200, 200, 10)

# Activation du mode automatique
automatique.activer()

print("Position initiale :", robot.obtenir_position())
print("Destination :", automatique.destination)

# Effectuer 10 déplacements
for i in range(10):

    decision = automatique.executer_decision()

    print(
        f"Étape {i + 1} :",
        decision,
        "| Position :",
        robot.obtenir_position()
    )

    if not automatique.actif:
        break

print("\nMessage :", automatique.message)