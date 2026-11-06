from obstacle import Obstacle

obstacle = Obstacle("O1", 5, 3, 2)

print(obstacle)

collision = obstacle.verifier_collision(5, 3, 2)

print("Collision détectée :", collision)