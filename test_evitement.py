from robot import Robot
from simulation import Simulation
from capteur import Capteur
from automatique import Automatique

# 1. Créer le robot
robot = Robot(
    x=300,
    y=200,
    z=40,
    angle=-90,
    vitesse=5,
    rayon=22
)

# 2. Créer l'environnement avec les obstacles
simulation = Simulation(800, 600, 300)

# 3. Créer le capteur
capteur = Capteur(portee=180)

# 4. Créer le contrôleur automatique
automatique = Automatique(robot, capteur, simulation)

# 5. Définir une destination située derrière l'obstacle O1
automatique.definir_destination(700, 200, 40)

# 6. Activer le mode automatique
automatique.activer()

print("POSITION INITIALE :", robot.obtenir_position())
print("DESTINATION : (700, 200, 40)")
print("--------------------------------")

for i in range(150):
    decision = automatique.executer_decision()
    position = robot.obtenir_position()

    print(
        f"Étape {i + 1} : {decision}",
        "| Position :", position
    )

    # Vérifier si le robot est entré en collision
    if simulation.verifier_collision(robot, *position):
        print("ALERTE : COLLISION DETECTEE !")
        break

    # Vérifier si la destination est atteinte
    if not automatique.actif:
        break

if not automatique.actif and decision == "DESTINATION_ATTEINTE":
    print("\nSUCCÈS : destination atteinte !")
elif automatique.actif:
    print("\nTEST TERMINÉ : nombre maximal d'étapes atteint.")