from obstacle import Obstacle


class Simulation:
    
    """
    Cette classe permet de gérer l'environnement de simulation
    dans lequel le robot effectue ses déplacements.
    Ses méthodes permettent de :
    - Initialiser les dimensions de l'environnement.
    - Ajouter de nouveaux obstacles.
    - Supprimer un obstacle à partir de son identifiant.
    - Vérifier les collisions entre le robot et les obstacles.
    - Vérifier que le robot reste dans les limites de l'environnement.
    - Récupérer la liste des obstacles présents.
    """
    

    def __init__(self, largeur=800, hauteur=600, profondeur=300):
        self.largeur = largeur
        self.hauteur = hauteur
        self.profondeur = profondeur

        self.obstacles = [
            Obstacle("O1", 450, 200, 0, 71),
            Obstacle("O2", 275, 435, 0, 83)
        ]

    def ajouter_obstacle(self, identifiant, x, y, z, rayon=2):
        """Ajoute un obstacle dans l'environnement."""

        if rayon <= 0:
            raise ValueError("Le rayon doit être positif.")

        if not (
            0 <= x <= self.largeur
            and 0 <= y <= self.hauteur
            and 0 <= z <= self.profondeur
        ):
            raise ValueError("La position de l'obstacle est invalide.")

        obstacle = Obstacle(identifiant, x, y, z, rayon)
        self.obstacles.append(obstacle)

        return obstacle

    def supprimer_obstacle(self, identifiant):
        """Supprime un obstacle grâce à son identifiant."""

        for obstacle in self.obstacles:
            if obstacle.identifiant == identifiant:
                self.obstacles.remove(obstacle)
                return True

        return False

    def verifier_collision(self, robot, x, y, z=0):
        """Vérifie les collisions en trois dimensions."""

        rayon = robot.rayon

        # Vérification des limites de l'environnement
        if (
            x - rayon < 0
            or x + rayon > self.largeur
            or y - rayon < 0
            or y + rayon > self.hauteur
            or z - rayon < 0
            or z + rayon > self.profondeur
        ):
            return True

        # Vérification des obstacles
        for obstacle in self.obstacles:
            if obstacle.verifier_collision(x, y, z, rayon):
                return True

        return False

    def obtenir_obstacles(self):
        """Retourne la liste des obstacles."""

        return self.obstacles