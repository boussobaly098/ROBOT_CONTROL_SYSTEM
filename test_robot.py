from robot import Robot

robot = Robot(x=0, y=0, z=0)

print("Position initiale :", robot.obtenir_position())

robot.monter()
print("Après montée :", robot.obtenir_position())

robot.descendre()
print("Après descente :", robot.obtenir_position())

robot.tourner_droite()
print("Direction :", robot.obtenir_direction())

print("Position calculée en avançant :", robot.avancer())