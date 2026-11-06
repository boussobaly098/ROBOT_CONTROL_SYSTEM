import math


class Robot:
    '''
    C'est la classe qui représente le robot et gère ses déplacements
    dans l'environnement de simulation.
    '''

    def __init__(
        self,
        x=0,
        y=0,
        z=0,
        angle=0,
        angle_vertical=0,
        vitesse=1,
        rayon=1
    ):
        # Coordonnees du robot
        self.x = x
        self.y = y
        self.z = z

        # Angles de deplacement
        self.angle = angle
        self.angle_vertical = angle_vertical

        # Sa vitesse et sa taille
        self.vitesse = vitesse
        self.rayon = rayon

        # Ceci indique si le robot peut se deplacer
        self.actif = True
    """
Les méthodes de cette classe permettent de contrôler le robot.
Elles permettent de :
- Déplacer le robot dans les trois dimensions (X, Y et Z).
- Avancer et reculer selon sa direction.
- Monter et descendre.
- Tourner à gauche et à droite.
- Incliner le robot vers le haut et vers le bas.
- Définir et récupérer sa position.
- Arrêter et reprendre le fonctionnement du robot.
"""
    def deplacer(self, dx, dy, dz):
        if not self.actif:
            return self.obtenir_position()

        self.x += dx
        self.y += dy
        self.z += dz

        return self.obtenir_position()

    def avancer(self):
        if not self.actif:
            return self.obtenir_position()

        angle_horizontal = math.radians(self.angle)
        angle_vertical = math.radians(self.angle_vertical)

        dx = self.vitesse * math.cos(angle_vertical) * math.cos(angle_horizontal)
        dy = self.vitesse * math.cos(angle_vertical) * math.sin(angle_horizontal)
        dz = self.vitesse * math.sin(angle_vertical)

        return (
            self.x + dx,
            self.y + dy,
            self.z + dz
        )

    def reculer(self):
        if not self.actif:
            return self.obtenir_position()

        angle_horizontal = math.radians(self.angle)
        angle_vertical = math.radians(self.angle_vertical)

        dx = self.vitesse * math.cos(angle_vertical) * math.cos(angle_horizontal)
        dy = self.vitesse * math.cos(angle_vertical) * math.sin(angle_horizontal)
        dz = self.vitesse * math.sin(angle_vertical)

        return (
            self.x - dx,
            self.y - dy,
            self.z - dz
        )

    def monter(self):
        return self.deplacer(0, 0, self.vitesse)

    def descendre(self):
        return self.deplacer(0, 0, -self.vitesse)

    def tourner_gauche(self):
        self.angle = (self.angle - 15) % 360

    def tourner_droite(self):
        self.angle = (self.angle + 15) % 360

    def incliner_haut(self):
        self.angle_vertical = min(90, self.angle_vertical + 15)

    def incliner_bas(self):
        self.angle_vertical = max(-90, self.angle_vertical - 15)

    def definir_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def obtenir_position(self):
        return self.x, self.y, self.z

    def obtenir_direction(self):
        return self.angle % 360

    def arreter(self):
        self.actif = False

    def reprendre(self):
        self.actif = True