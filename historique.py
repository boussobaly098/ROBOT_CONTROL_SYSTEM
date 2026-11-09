import math


class Historique:
    """Enregistre les positions successives du robot."""

    def __init__(self):
        self.positions = []
        self.distance_totale = 0.0

    @staticmethod
    def distance_entre(a, b):
        return math.sqrt(
            (b[0] - a[0]) ** 2
            + (b[1] - a[1]) ** 2
            + (b[2] - a[2]) ** 2
        )

    def enregistrer_position(
        self, x, y, z, action="Déplacement", forcer=False
    ):
        nouvelle = (x, y, z)

        if self.positions:
            derniere = self.positions[-1]["position"]
            deplacement = self.distance_entre(derniere, nouvelle)

            if deplacement < 1e-9 and not forcer:
                return False

            self.distance_totale += deplacement

        self.positions.append({
            "position": nouvelle,
            "action": action,
            "distance": self.distance_totale
        })
        return True

    def calculer_distance(self):
        return self.distance_totale

    def nombre_positions(self):
        return len(self.positions)

    def obtenir_positions(self):
        return [element["position"] for element in self.positions]

    def afficher_parcours(self):
        lignes = [
            f"{'N°':>4} | {'Action':<16} | {'X':>8} | {'Y':>8} | "
            f"{'Z':>8} | {'Distance':>9}",
            "-" * 68
        ]

        for numero, element in enumerate(self.positions, start=1):
            x, y, z = element["position"]
            lignes.append(
                f"{numero:>4} | {element['action']:<16} | "
                f"{x:>8.1f} | {y:>8.1f} | {z:>8.1f} | "
                f"{element['distance']:>9.1f}"
            )

        return lignes

    def reinitialiser(self):
        self.positions = []
        self.distance_totale = 0.0