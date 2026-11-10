# Robot Control System

Application de simulation et de contrôle d'un robot mobile en 3D, avec détection
et évitement d'obstacles. Projet académique, Licence 2 Informatique et
Télécommunication, Université Cheikh Ahmadoul Khadim (UCAK).

**Auteur :** Serigne Modou Bousso
**Encadrant :** Dr Mame A. DIAW

![Interface](docs/capture.png)

## Fonctionnalités

- Commande manuelle : avancer, reculer, tourner, monter, descendre, incliner
- Capteur de distance (portée 180) : LIBRE (> 90), ATTENTION (41 à 90), DANGER (≤ 40)
- Mode automatique : chemin calculé avec l'algorithme A* sur une grille 3D,
  simplifié en lignes droites, recalculé si un obstacle gêne
- Arrêt d'urgence, reprise et réinitialisation
- Historique des positions et distance parcourue
- Tracé du trajet qui s'estompe
- Configuration du scénario (robot, obstacles O1 et O2, destination)
- Ajout et suppression d'obstacles depuis l'interface

## Lancer le projet

Python 3.8 ou plus récent (tkinter est inclus avec Python).

```bash
git clone https://github.com/<votre-nom>/robot-control-system.git
cd robot-control-system
python main.py
```

Sous Linux, si tkinter manque : `sudo apt install python3-tk`

## Architecture (POO)

| Classe | Rôle |
|---|---|
| `Robot` | position, direction, déplacements, arrêt et reprise |
| `Obstacle` | obstacle sphérique et test de collision |
| `Capteur` | mesure de distance et niveau de danger |
| `Simulation` | environnement 800 x 600 x 300 et collisions |
| `Automatique` | navigation A* et suivi du chemin |
| `Historique` | enregistrement des positions et distance totale |
| `InterfaceGraphique` | affichage et commandes (tkinter) |

Les classes collaborent par composition : par exemple `Automatique` utilise un
`Robot`, un `Capteur` et une `Simulation`.

## Utilisation

1. Saisir la destination (X, Y, Z) ou ouvrir « Configuration du scénario ».
2. Cliquer sur « Mode automatique » : le robot rejoint la destination.
3. Si aucun passage n'existe, le robot signale qu'il est bloqué.
