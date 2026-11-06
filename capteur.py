import math


class Capteur:
    """
    Capteur de distance du robot.
    Détecte les obstacles dans un environnement 3D.
    """

    def __init__(self, portee=180):
        self.portee = portee

    def mesurer_distance(
        self, robot, obstacles, largeur, hauteur, profondeur
    ):
        """
        Mesure la distance jusqu'au premier obstacle
        rencontré dans la direction du robot.
        """

        angle_horizontal = math.radians(robot.angle)
        angle_vertical = math.radians(robot.angle_vertical)

        # Direction du faisceau en 3D
        direction_x = (
            math.cos(angle_vertical) * math.cos(angle_horizontal)
        )
        direction_y = (
            math.cos(angle_vertical) * math.sin(angle_horizontal)
        )
        direction_z = math.sin(angle_vertical)

        distance = 0

        while distance <= self.portee:

            x = robot.x + distance * direction_x
            y = robot.y + distance * direction_y
            z = robot.z + distance * direction_z

            # Vérification des limites de l'environnement
            if (
                x <= 0 or x >= largeur
                or y <= 0 or y >= hauteur
                or z <= 0 or z >= profondeur
            ):
                return distance

            # Vérification des obstacles 3D
            for obstacle in obstacles:

                collision = obstacle.verifier_collision(
                    x, y, z, rayon_robot=0
                )

                if collision:
                    return distance

            distance += 5

        return self.portee

    def detecter_obstacle(self, distance):
        """Détermine le niveau de danger."""

        if distance <= 40:
            return "DANGER"

        elif distance <= 90:
            return "ATTENTION"

        else:
            return "LIBRE"