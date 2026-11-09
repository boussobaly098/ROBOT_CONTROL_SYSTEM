import heapq
import math


class Automatique:
    """
    Contrôleur automatique du robot 3D.

    Il calcule une trajectoire sans collision avec l'algorithme A*
    sur une grille 3D, la simplifie (lignes droites quand c'est possible),
    puis fait avancer le robot pas à pas le long de cette trajectoire.
    Si un obstacle apparaît sur le chemin, la trajectoire est recalculée.
    """

    # Taille d'une case de la grille de recherche A*
    PAS_GRILLE = 20

    def __init__(self, robot, capteur, simulation):
        self.robot = robot
        self.capteur = capteur
        self.simulation = simulation

        self.actif = False
        self.message = "Mode automatique désactivé"

        self.destination = None
        self.tolerance = 3

        # Points restant à atteindre (le dernier est la destination)
        self.trajectoire = []

    # ==========================================
    # DESTINATION ET ETAT
    # ==========================================

    def definir_destination(self, x, y, z):
        if not (
            0 <= x <= self.simulation.largeur
            and 0 <= y <= self.simulation.hauteur
            and 0 <= z <= self.simulation.profondeur
        ):
            raise ValueError("Destination en dehors de l'environnement.")

        self.destination = (x, y, z)
        self.trajectoire = []
        self.message = f"Destination définie : {self.destination}"

    def activer(self):
        if self.destination is None:
            self.message = "Veuillez définir une destination."
            return

        self.trajectoire = []
        self.actif = True
        self.message = "Mode automatique activé"

    def desactiver(self):
        self.actif = False
        self.trajectoire = []
        self.message = "Mode automatique désactivé"

    # ==========================================
    # OUTILS
    # ==========================================

    @staticmethod
    def _distance(a, b):
        return math.sqrt(
            (b[0] - a[0]) ** 2
            + (b[1] - a[1]) ** 2
            + (b[2] - a[2]) ** 2
        )

    def calculer_distance_destination(self):
        if self.destination is None:
            return 0

        return self._distance(
            self.robot.obtenir_position(), self.destination
        )

    def _libre(self, x, y, z):
        """Vrai si le robot peut se trouver à cette position."""
        return not self.simulation.verifier_collision(
            self.robot, x, y, z
        )

    def _segment_libre(self, a, b):
        """Vrai si le robot peut aller en ligne droite de a à b."""

        longueur = self._distance(a, b)
        etapes = max(1, int(longueur / 5))

        for i in range(1, etapes + 1):
            t = i / etapes

            if not self._libre(
                a[0] + (b[0] - a[0]) * t,
                a[1] + (b[1] - a[1]) * t,
                a[2] + (b[2] - a[2]) * t
            ):
                return False

        return True

    # ==========================================
    # CALCUL DE LA TRAJECTOIRE (A*)
    # ==========================================

    def calculer_trajectoire(self):
        """
        Calcule une trajectoire sans collision entre la position
        du robot et la destination. Retourne True si elle existe.
        """

        depart = self.robot.obtenir_position()
        arrivee = self.destination

        # 1. Si la ligne droite est libre, pas besoin de chercher
        if self._segment_libre(depart, arrivee):
            self.trajectoire = [arrivee]
            return True

        # 2. Sinon, A* sur une grille 3D ancrée sur le robot
        pas = self.PAS_GRILLE

        def position(noeud):
            return (
                depart[0] + noeud[0] * pas,
                depart[1] + noeud[1] * pas,
                depart[2] + noeud[2] * pas
            )

        cache = {}

        def libre(noeud):
            if noeud not in cache:
                cache[noeud] = self._libre(*position(noeud))
            return cache[noeud]

        # Case d'arrivée : la case libre la plus proche de la destination
        centre = tuple(
            round((arrivee[i] - depart[i]) / pas) for i in range(3)
        )

        candidats = sorted(
            (
                (centre[0] + a, centre[1] + b, centre[2] + c)
                for a in (-1, 0, 1)
                for b in (-1, 0, 1)
                for c in (-1, 0, 1)
            ),
            key=lambda n: self._distance(position(n), arrivee)
        )

        but = next((n for n in candidats if libre(n)), None)

        if but is None:
            return False

        position_but = position(but)

        def heuristique(noeud):
            return self._distance(position(noeud), position_but)

        voisins = [
            (a, b, c)
            for a in (-1, 0, 1)
            for b in (-1, 0, 1)
            for c in (-1, 0, 1)
            if (a, b, c) != (0, 0, 0)
        ]
        couts = {
            v: math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) * pas
            for v in voisins
        }

        origine = (0, 0, 0)
        ouvert = [(heuristique(origine), 0.0, origine)]
        meilleur_cout = {origine: 0.0}
        parent = {}
        ferme = set()

        while ouvert:
            _, cout, noeud = heapq.heappop(ouvert)

            if noeud in ferme:
                continue

            ferme.add(noeud)

            if noeud == but:
                break

            for v in voisins:
                suivant = (
                    noeud[0] + v[0],
                    noeud[1] + v[1],
                    noeud[2] + v[2]
                )

                if suivant in ferme or not libre(suivant):
                    continue

                nouveau_cout = cout + couts[v]

                if nouveau_cout < meilleur_cout.get(suivant, float("inf")):
                    meilleur_cout[suivant] = nouveau_cout
                    parent[suivant] = noeud
                    heapq.heappush(
                        ouvert,
                        (
                            nouveau_cout + heuristique(suivant),
                            nouveau_cout,
                            suivant
                        )
                    )
        else:
            # La recherche s'est terminée sans atteindre la case d'arrivée
            return False

        # 3. Reconstruire le chemin
        chemin = [but]

        while chemin[-1] != origine:
            chemin.append(parent[chemin[-1]])

        chemin.reverse()

        points = (
            [depart]
            + [position(n) for n in chemin[1:]]
            + [arrivee]
        )

        # 4. Simplifier : sauter les points inutiles
        simplifie = [points[0]]
        i = 0

        while i < len(points) - 1:
            j = len(points) - 1

            while j > i + 1 and not self._segment_libre(
                points[i], points[j]
            ):
                j -= 1

            simplifie.append(points[j])
            i = j

        self.trajectoire = simplifie[1:]
        return True

    # ==========================================
    # SUIVI DE LA TRAJECTOIRE
    # ==========================================

    def _nettoyer_trajectoire(self):
        """Retire les points déjà atteints."""

        position = self.robot.obtenir_position()

        while self.trajectoire and self._distance(
            position, self.trajectoire[0]
        ) < 1e-6:
            self.trajectoire.pop(0)

    def _pas(self):
        """Déplacement (dx, dy, dz) vers le prochain point."""

        position = self.robot.obtenir_position()
        cible = self.trajectoire[0]
        distance = self._distance(position, cible)

        if distance < 1e-9:
            return (0, 0, 0)

        pas = min(self.robot.vitesse, distance)
        facteur = pas / distance

        return (
            (cible[0] - position[0]) * facteur,
            (cible[1] - position[1]) * facteur,
            (cible[2] - position[2]) * facteur
        )

    def _pas_libre(self):
        """Vrai si le prochain pas ne provoque pas de collision."""

        x, y, z = self.robot.obtenir_position()
        dx, dy, dz = self._pas()

        return self._libre(x + dx, y + dy, z + dz)

    def prendre_decision(self):
        if not self.actif or self.destination is None:
            return "ARRET"

        if self.calculer_distance_destination() <= self.tolerance:
            self.actif = False
            self.trajectoire = []
            self.message = "Destination atteinte !"
            return "DESTINATION_ATTEINTE"

        self._nettoyer_trajectoire()

        # Calculer (ou recalculer) la trajectoire si nécessaire
        if not self.trajectoire or not self._pas_libre():

            if not self.calculer_trajectoire():
                self.trajectoire = []
                self.message = "Aucun passage libre détecté"
                return "OBSTACLE"

            self._nettoyer_trajectoire()

            if not self.trajectoire or not self._pas_libre():
                self.trajectoire = []
                self.message = "Déplacement bloqué par sécurité"
                return "OBSTACLE"

        # Orienter le robot vers le prochain point
        x, y, z = self.robot.obtenir_position()
        cible = self.trajectoire[0]

        dx = cible[0] - x
        dy = cible[1] - y
        dz = cible[2] - z
        distance_h = math.sqrt(dx ** 2 + dy ** 2)

        if distance_h > 1e-9:
            self.robot.angle = math.degrees(math.atan2(dy, dx)) % 360

        self.robot.angle_vertical = math.degrees(
            math.atan2(dz, distance_h)
        )

        # Comparer avec la direction directe vers la destination
        ex = self.destination[0] - x
        ey = self.destination[1] - y
        ez = self.destination[2] - z

        angle_voulu = math.degrees(math.atan2(ey, ex))
        vertical_voulu = math.degrees(
            math.atan2(ez, math.sqrt(ex ** 2 + ey ** 2))
        )

        ecart_h = abs((self.robot.angle - angle_voulu + 180) % 360 - 180)
        ecart_v = abs(self.robot.angle_vertical - vertical_voulu)

        if ecart_h > 1 or ecart_v > 1:
            return "EVITER"

        return "AVANCER"

    def executer_decision(self):
        decision = self.prendre_decision()

        if decision in ("AVANCER", "EVITER"):

            x, y, z = self.robot.obtenir_position()
            dx, dy, dz = self._pas()

            if self.simulation.verifier_collision(
                self.robot, x + dx, y + dy, z + dz
            ):
                self.trajectoire = []
                self.message = "Déplacement bloqué par sécurité"
                return "OBSTACLE"

            self.robot.deplacer(dx, dy, dz)
            self._nettoyer_trajectoire()

            if decision == "EVITER":
                self.message = "Obstacle détecté : changement de direction"
            else:
                self.message = "Robot en déplacement automatique"

        elif decision == "DESTINATION_ATTEINTE":
            self.message = "Destination atteinte !"

        elif decision == "OBSTACLE":
            self.message = "Aucun passage libre : robot en attente"

        elif decision == "ARRET":
            self.message = "Mode automatique arrêté"

        return decision