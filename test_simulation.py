from robot import Robot
from simulation import Simulation

robot = Robot(x=0, y=0, z=0)
simulation = Simulation()

print("Nombre d'obstacles :", len(simulation.obtenir_obstacles()))

print("\nListe des obstacles :")
for obstacle in simulation.obtenir_obstacles():
    print(obstacle)

print("\nTest de collision :")

print(
    "Position (450, 200, 0) :",
    simulation.verifier_collision(robot, 450, 200, 0)
)

print(
    "Position (0, 0, 0) :",
    simulation.verifier_collision(robot, 1, 1, 1)
)

print("\nAjout d'un obstacle :")
simulation.ajouter_obstacle("O3", 100, 100, 50, 5)

print("Nombre après ajout :", len(simulation.obtenir_obstacles()))

print("\nSuppression de O3 :")
simulation.supprimer_obstacle("O3")

print("Nombre après suppression :", len(simulation.obtenir_obstacles()))