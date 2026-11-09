import tkinter as tk

from robot import Robot
from capteur import Capteur
from simulation import Simulation
from automatique import Automatique
from historique import Historique
from interface import InterfaceGraphique


def main():

    # Création de la fenêtre principale
    fenetre = tk.Tk()

    # Création des objets du système
    robot = Robot(
        x=300, y=300, z=40, angle=-90, vitesse=15, rayon=22
    )

    capteur = Capteur(portee=180)

    simulation = Simulation(
        largeur=800,
        hauteur=600
    )

    automatique = Automatique(
        robot,
        capteur,
        simulation
    )

    historique = Historique()

    # Création de l'interface graphique
    interface = InterfaceGraphique(
        fenetre,
        robot,
        capteur,
        simulation,
        automatique,
        historique
    )

    # Lancement de l'application
    fenetre.mainloop()


if __name__ == "__main__":
    main()