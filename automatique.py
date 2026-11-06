import math


class Automatique:
    """
    Contrôleur automatique du robot 3D.
    Recherche une direction libre pour atteindre la destination.
    """

    def __init__(self, robot, capteur, simulation):
        self.robot = robot
        self.capteur = capteur
        self.simulation = simulation

        self.actif = False
        self.message = "Mode automatique désactivé"

        self.destination = None
        self.tolerance = 3

    def definir_destination(self, x, y, z):
        if not (
            0 <= x <= self.simulation.largeur
            and 0 <= y <= self.simulation.hauteur
            and 0 <= z <= self.simulation.profondeur
        ):
            raise ValueError("Destination en dehors de l'environnement.")

        self.destination = (x, y, z)
        self.message = f"Destination définie : {self.destination}"

    def activer(self):
        if self.destination is None:
            self.message = "Veuillez définir une destination."
            return

        self.actif = True
        self.message = "Mode automatique activé"

    def desactiver(self):
        self.actif = False
        self.message = "Mode automatique désactivé"

    def calculer_distance_destination(self):
        if self.destination is None:
            return 0

        x, y, z = self.destination

        return math.sqrt(
            (x - self.robot.x) ** 2
            + (y - self.robot.y) ** 2
            + (z - self.robot.z) ** 2
        )

    def prendre_decision(self):
        if not self.actif or self.destination is None:
            return "ARRET"

        distance_destination = self.calculer_distance_destination()

        if distance_destination <= self.tolerance:
            self.actif = False
            self.message = "Destination atteinte !"
            return "DESTINATION_ATTEINTE"

        # Calcul de la direction vers la destination
        dx = self.destination[0] - self.robot.x
        dy = self.destination[1] - self.robot.y
        dz = self.destination[2] - self.robot.z

        distance_horizontale = math.sqrt(dx ** 2 + dy ** 2)

        angle_voulu = math.degrees(math.atan2(dy, dx))
        angle_vertical = math.degrees(
            math.atan2(dz, distance_horizontale)
        )

        # Directions que le robot peut essayer
        decalages = [
            0, 15, -15, 30, -30, 45, -45,
            60, -60, 90, -90, 135, -135, 180
        ]

        meilleure_score = float("inf")
        meilleur_angle = None
        meilleur_vertical = angle_vertical

        pas = min(self.robot.vitesse, distance_destination)

        for decalage in decalages:

            angle = (angle_voulu + decalage) % 360

            angle_rad = math.radians(angle)
            vertical_rad = math.radians(angle_vertical)

            # Calcul du prochain déplacement
            mouvement_x = (
                pas * math.cos(vertical_rad) * math.cos(angle_rad)
            )
            mouvement_y = (
                pas * math.cos(vertical_rad) * math.sin(angle_rad)
            )
            mouvement_z = pas * math.sin(vertical_rad)

            nouveau_x = self.robot.x + mouvement_x
            nouveau_y = self.robot.y + mouvement_y
            nouveau_z = self.robot.z + mouvement_z

            # Vérifier si le déplacement provoquerait une collision
            if self.simulation.verifier_collision(
                self.robot, nouveau_x, nouveau_y, nouveau_z
            ):
                continue

            # Tester la visibilité dans cette direction
            ancien_angle = self.robot.angle
            ancien_angle_vertical = self.robot.angle_vertical

            self.robot.angle = angle
            self.robot.angle_vertical = angle_vertical

            distance_capteur = self.capteur.mesurer_distance(
                self.robot,
                self.simulation.obtenir_obstacles(),
                self.simulation.largeur,
                self.simulation.hauteur,
                self.simulation.profondeur
            )

            # Restaurer les anciennes directions
            self.robot.angle = ancien_angle
            self.robot.angle_vertical = ancien_angle_vertical
             

            # Ne pas choisir une direction immédiatement bloquée
            if distance_capteur <= self.robot.rayon:
                continue

            # Calculer la distance restante après ce déplacement
            distance_restante = math.sqrt(
                (self.destination[0] - nouveau_x) ** 2
                + (self.destination[1] - nouveau_y) ** 2
                + (self.destination[2] - nouveau_z) ** 2
            )

            # Privilégier la progression et les petits changements d'angle
            score = distance_restante + abs(decalage) * 0.05

            if score < meilleure_score:
                meilleure_score = score
                meilleur_angle = angle
                meilleur_vertical = angle_vertical

        if meilleur_angle is None:
            self.message = "Aucun passage libre détecté"
            return "OBSTACLE"

        # Appliquer la meilleure direction
        self.robot.angle = meilleur_angle
        self.robot.angle_vertical = meilleur_vertical

        if abs((meilleur_angle - angle_voulu + 180) % 360 - 180) > 1:
            return "EVITER"

        return "AVANCER"

    def executer_decision(self):
        decision = self.prendre_decision()

        if decision in ("AVANCER", "EVITER"):

            distance = self.calculer_distance_destination()
            vitesse = min(self.robot.vitesse, distance)

            angle_h = math.radians(self.robot.angle)
            angle_v = math.radians(self.robot.angle_vertical)

            dx = vitesse * math.cos(angle_v) * math.cos(angle_h)
            dy = vitesse * math.cos(angle_v) * math.sin(angle_h)
            dz = vitesse * math.sin(angle_v)

            nouveau_x = self.robot.x + dx
            nouveau_y = self.robot.y + dy
            nouveau_z = self.robot.z + dz

            if not self.simulation.verifier_collision(
                self.robot, nouveau_x, nouveau_y, nouveau_z
            ):
                self.robot.deplacer(dx, dy, dz)

                if decision == "EVITER":
                    self.message = "Obstacle détecté : changement de direction"
                else:
                    self.message = "Robot en déplacement automatique"

            else:
                self.message = "Déplacement bloqué par sécurité"
                return "OBSTACLE"

        elif decision == "DESTINATION_ATTEINTE":
            self.message = "Destination atteinte !"

        elif decision == "OBSTACLE":
            self.message = "Aucun passage libre : robot en attente"

        elif decision == "ARRET":
            self.message = "Mode automatique arrêté"

        return decision