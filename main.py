import tkinter as tk

from robot import Robot
from capteur import Capteur
from simulation import Simulation
from automatique import Automatique
from interface import InterfaceGraphique


def main():

    # Pour la creation de la fenetre principale
    fenetre = tk.Tk()

    # Celle des objets du système
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

    # Celle de l'interface graphique
    interface = InterfaceGraphique(
        fenetre,
        robot,
        capteur,
        simulation,
        automatique
    )

    # Pour l'encer l;application
    fenetre.mainloop()


if __name__ == "__main__":
    main()