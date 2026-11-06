import math


class Obstacle:

    """ 
      Cette classe représente un obstacle dans l'environnement
      de simulation.
      Ses méthodes permettent de :
    - Initialiser un obstacle avec son identifiant.
    - Définir sa position dans les trois dimensions.
    - Récupérer ses coordonnées.
    - Vérifier si le robot entre en collision avec lui.
    - Afficher les informations concernant l'obstacle.
    """   

    def __init__(self, identifiant, x, y, z, rayon=2):
        self.identifiant = identifiant
        self.x = x
        self.y = y
        self.z = z
        self.rayon = rayon

    def obtenir_position(self):
        return (self.x, self.y, self.z)

    def verifier_collision(self, x, y, z, rayon_robot=1):
        distance = math.sqrt(
            (x - self.x) ** 2 +
            (y - self.y) ** 2 +
            (z - self.z) ** 2
        )

        return distance <= self.rayon + rayon_robot

    def __str__(self):
        return (
            f"Obstacle {self.identifiant} : "
            f"Position {self.obtenir_position()}, "
            f"Rayon {self.rayon}"
        )