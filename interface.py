import tkinter as tk
import math
from tkinter import messagebox

class InterfaceGraphique:

    def __init__(self, fenetre, robot, capteur, simulation, automatique):
        self.fenetre = fenetre
        self.robot = robot
        self.capteur = capteur
        self.simulation = simulation
        self.automatique = automatique

        self.FOND = "#0F172A"
        self.PANNEAU = "#1E293B"
        self.CYAN = "#22D3EE"
        self.BLANC = "#F8FAFC"
        self.VERT = "#22C55E"
        self.ORANGE = "#F59E0B"
        self.ROUGE = "#EF4444"

        self.fenetre.title("ROBOT CONTROL SYSTEM")
        self.fenetre.geometry("1400x850")
        self.fenetre.minsize(950, 650)
        self.fenetre.configure(bg=self.FOND)

        self.auto_en_cours = False
        self.identifiant_boucle = None
        self.position_initiale = (
    self.robot.x,
    self.robot.y,
    self.robot.z
)

        self.creer_interface()
    # Actualiser après la création complète de la fenêtre
        self.fenetre.after(100, self.actualiser)

    # ==========================================
    # CREATION DE L'INTERFACE
    # ==========================================

    def creer_interface(self):

        titre = tk.Label(
            self.fenetre,
            text="ROBOT CONTROL SYSTEM",
            font=("Arial", 22, "bold"),
            bg=self.FOND,
            fg=self.CYAN
        )
        titre.pack(pady=12)

        contenu = tk.Frame(self.fenetre, bg=self.FOND)
        contenu.pack(fill="both", expand=True, padx=15, pady=10)

        # Zone de simulation
        zone_simulation = tk.Frame(contenu, bg=self.PANNEAU)
        zone_simulation.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.canvas = tk.Canvas(
            zone_simulation,
            bg="#111827",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas.bind(
        "<Configure>",
        lambda evenement: self.fenetre.after_idle(self.actualiser)
)

        # Panneau de commandes
        panneau = tk.Frame(
            contenu,
            bg=self.PANNEAU,
            width=290
        )
        panneau.pack(side="right", fill="y")
        panneau.pack_propagate(False)

        self.creer_commandes(panneau)
        
    # ==========================================
    # CREATION DES COMMANDES
    # ==========================================

    def creer_commandes(self, panneau):

        tk.Label(
            panneau,
            text="COMMANDES DU ROBOT",
            font=("Arial", 13, "bold"),
            bg=self.PANNEAU,
            fg=self.CYAN
        ).pack(pady=12)

        self.creer_bouton(
            panneau,
            "CONFIGURATION DU SCÉNARIO",
            self.ouvrir_configuration,
            self.ORANGE
        )

        # Déplacement horizontal
        tk.Label(
            panneau,
            text="Déplacement",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        cadre_direction = tk.Frame(panneau, bg=self.PANNEAU)
        cadre_direction.pack(pady=5)

        self.creer_bouton(
            cadre_direction, "AVANCER", lambda: self.commander("AVANCER"),
            self.VERT, 0, 1
        )
        self.creer_bouton(
            cadre_direction, "GAUCHE", lambda: self.commander("GAUCHE"),
            self.CYAN, 1, 0
        )
        self.creer_bouton(
            cadre_direction, "DROITE", lambda: self.commander("DROITE"),
            self.CYAN, 1, 2
        )
        self.creer_bouton(
            cadre_direction, "RECULER", lambda: self.commander("RECULER"),
            self.ORANGE, 2, 1
        )

        # Déplacement vertical
        tk.Label(
            panneau,
            text="Déplacement vertical",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 11, "bold")
        ).pack(pady=(12, 5))

        cadre_vertical = tk.Frame(panneau, bg=self.PANNEAU)
        cadre_vertical.pack()

        self.creer_bouton(
            cadre_vertical, "MONTER", lambda: self.commander("MONTER"),
            self.VERT, 0, 0
        )
        self.creer_bouton(
            cadre_vertical, "DESCENDRE", lambda: self.commander("DESCENDRE"),
            self.ORANGE, 0, 1
        )

        # Inclinaison
        cadre_inclinaison = tk.Frame(panneau, bg=self.PANNEAU)
        cadre_inclinaison.pack(pady=5)

        self.creer_bouton(
            cadre_inclinaison, "HAUT", lambda: self.commander("HAUT"),
            self.CYAN, 0, 0
        )
        self.creer_bouton(
            cadre_inclinaison, "BAS", lambda: self.commander("BAS"),
            self.CYAN, 0, 1
        )

        # Destination
        tk.Label(
            panneau,
            text="DESTINATION (X, Y, Z)",
            font=("Arial", 11, "bold"),
            bg=self.PANNEAU,
            fg=self.CYAN
        ).pack(pady=(15, 5))

        cadre_destination = tk.Frame(panneau, bg=self.PANNEAU)
        cadre_destination.pack()

        self.entree_x = self.creer_champ(
            cadre_destination, "X", "700", 0
        )
        self.entree_y = self.creer_champ(
            cadre_destination, "Y", "300", 1
        )
        self.entree_z = self.creer_champ(
            cadre_destination, "Z", "40", 2
        )

        self.bouton_auto = tk.Button(
            panneau,
            text="MODE AUTOMATIQUE",
            command=self.activer_automatique,
            bg=self.VERT,
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        )
        self.bouton_auto.pack(fill="x", padx=15, pady=10)

        # Arrêt et réinitialisation
        self.creer_bouton(
            panneau, "ARRÊT D'URGENCE", self.arreter,
            self.ROUGE
        )

        self.creer_bouton(
            panneau, "RÉINITIALISER", self.reinitialiser,
            "#475569"
        )

        # Informations
        tk.Label(
            panneau,
            text="INFORMATIONS",
            font=("Arial", 12, "bold"),
            bg=self.PANNEAU,
            fg=self.CYAN
        ).pack(pady=(18, 8))

        self.label_position = tk.Label(
            panneau,
            text="Position : X=0 Y=0 Z=0",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 10)
        )
        self.label_position.pack(pady=4)

        self.label_direction = tk.Label(
            panneau,
            text="Direction : 0°",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 10)
        )
        self.label_direction.pack(pady=4)

        self.label_capteur = tk.Label(
            panneau,
            text="Capteur : LIBRE",
            bg=self.PANNEAU,
            fg=self.VERT,
            font=("Arial", 10, "bold")
        )
        self.label_capteur.pack(pady=4)

        self.label_statut = tk.Label(
            panneau,
            text="Système prêt",
            bg=self.PANNEAU,
            fg=self.VERT,
            font=("Arial", 10, "bold"),
            wraplength=250
        )
        self.label_statut.pack(pady=12)

    def creer_champ(self, parent, nom, valeur, colonne):

        cadre = tk.Frame(parent, bg=self.PANNEAU)
        cadre.grid(row=0, column=colonne, padx=4)

        tk.Label(
            cadre,
            text=nom,
            bg=self.PANNEAU,
            fg=self.BLANC
        ).pack()

        entree = tk.Entry(
            cadre,
            width=7,
            justify="center"
        )
        entree.insert(0, valeur)
        entree.pack(pady=3)

        return entree

    def creer_bouton(
        self, parent, texte, commande, couleur,
        ligne=None, colonne=None
    ):

        bouton = tk.Button(
            parent,
            text=texte,
            command=commande,
            bg=couleur,
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=7
        )

        if ligne is not None and colonne is not None:
            bouton.grid(
                row=ligne,
                column=colonne,
                padx=3,
                pady=3,
                sticky="ew"
            )
        else:
            bouton.pack(fill="x", padx=15, pady=5)

        return bouton

    # ==========================================
    # PROJECTION DES COORDONNEES 3D
    # ==========================================

    def projeter(self, x, y, z):

        largeur = max(self.canvas.winfo_width(), 1)
        hauteur = max(self.canvas.winfo_height(), 1)

        echelle_x = largeur / self.simulation.largeur
        echelle_y = hauteur / self.simulation.hauteur

        ecran_x = x * echelle_x + z * 0.25
        ecran_y = y * echelle_y - z * 0.40

        return ecran_x, ecran_y

    # ==========================================
    # DESSIN DE L'ENVIRONNEMENT
    # ==========================================

    def dessiner_simulation(self):

        self.canvas.delete("all")

        largeur = self.canvas.winfo_width()
        hauteur = self.canvas.winfo_height()

        if largeur <= 1 or hauteur <= 1:
            return

        # Grille
        pas = 50

        for x in range(0, self.simulation.largeur + 1, pas):
            sx1, sy1 = self.projeter(x, 0, 0)
            sx2, sy2 = self.projeter(x, self.simulation.hauteur, 0)

            self.canvas.create_line(
                sx1, sy1, sx2, sy2,
                fill="#263449"
            )

        for y in range(0, self.simulation.hauteur + 1, pas):
            sx1, sy1 = self.projeter(0, y, 0)
            sx2, sy2 = self.projeter(
                self.simulation.largeur, y, 0
            )

            self.canvas.create_line(
                sx1, sy1, sx2, sy2,
                fill="#263449"
            )

        # Limites de l'environnement
        coins = [
            self.projeter(0, 0, 0),
            self.projeter(self.simulation.largeur, 0, 0),
            self.projeter(
                self.simulation.largeur,
                self.simulation.hauteur, 0
            ),
            self.projeter(0, self.simulation.hauteur, 0)
        ]

        self.canvas.create_polygon(
            [coord for point in coins for coord in point],
            outline=self.CYAN,
            fill="",
            width=2
        )

        # Obstacles
        for obstacle in self.simulation.obtenir_obstacles():

            ox, oy = self.projeter(
                obstacle.x, obstacle.y, obstacle.z
            )

            rayon_x = obstacle.rayon * (
                largeur / self.simulation.largeur
            )
            rayon_y = obstacle.rayon * (
                hauteur / self.simulation.hauteur
            )

            # Ombre de l'obstacle au sol
            sol_x, sol_y = self.projeter(
                obstacle.x, obstacle.y, 0
            )

            self.canvas.create_oval(
                sol_x - rayon_x,
                sol_y - rayon_y * 0.45,
                sol_x + rayon_x,
                sol_y + rayon_y * 0.45,
                fill="#374151",
                outline=""
            )

            # Corps de l'obstacle
            self.canvas.create_oval(
                ox - rayon_x,
                oy - rayon_y,
                ox + rayon_x,
                oy + rayon_y,
                fill="#64748B",
                outline=self.ROUGE,
                width=2
            )

            self.canvas.create_text(
                ox,
                oy,
                text=obstacle.identifiant,
                fill=self.BLANC,
                font=("Arial", 9, "bold")
            )

        # Repère
        self.canvas.create_text(
            65, 20,
            text="ENVIRONNEMENT 3D",
            fill=self.CYAN,
            font=("Arial", 12, "bold")
        )

    # ==========================================
    # DESSIN DU ROBOT ET DU CAPTEUR
    # ==========================================

    def dessiner_robot(self):

        x, y, z = self.robot.obtenir_position()
        ecran_x, ecran_y = self.projeter(x, y, z)

        # Mesure du capteur
        distance = self.capteur.mesurer_distance(
            self.robot,
            self.simulation.obtenir_obstacles(),
            self.simulation.largeur,
            self.simulation.hauteur,
            self.simulation.profondeur
        )

        etat = self.capteur.detecter_obstacle(distance)

        if etat == "DANGER":
            couleur_capteur = self.ROUGE
        elif etat == "ATTENTION":
            couleur_capteur = self.ORANGE
        else:
            couleur_capteur = self.VERT

        # Direction du capteur
        angle_h = math.radians(self.robot.angle)
        angle_v = math.radians(self.robot.angle_vertical)

        dx = math.cos(angle_v) * math.cos(angle_h)
        dy = math.cos(angle_v) * math.sin(angle_h)
        dz = math.sin(angle_v)

        fin_x = x + distance * dx
        fin_y = y + distance * dy
        fin_z = z + distance * dz

        fin_ecran_x, fin_ecran_y = self.projeter(
            fin_x, fin_y, fin_z
        )

        # Faisceau du capteur
        self.canvas.create_line(
            ecran_x, ecran_y,
            fin_ecran_x, fin_ecran_y,
            fill=couleur_capteur,
            width=2,
            dash=(5, 3)
        )

        # Point lumineux à l'extrémité du capteur
        self.canvas.create_oval(
            fin_ecran_x - 5,
            fin_ecran_y - 5,
            fin_ecran_x + 5,
            fin_ecran_y + 5,
            fill=couleur_capteur,
            outline=""
        )

        # Liaison verticale entre le sol et le robot
        sol_x, sol_y = self.projeter(x, y, 0)

        self.canvas.create_line(
            sol_x, sol_y,
            ecran_x, ecran_y,
            fill=self.CYAN,
            dash=(3, 3)
        )

        # Ombre du robot
        self.canvas.create_oval(
            sol_x - 20, sol_y - 9,
            sol_x + 20, sol_y + 9,
            fill="#374151",
            outline=""
        )

        # Corps du robot
        rayon = 22

        self.canvas.create_oval(
            ecran_x - rayon,
            ecran_y - rayon,
            ecran_x + rayon,
            ecran_y + rayon,
            fill="#2563EB",
            outline=self.CYAN,
            width=3
        )

        # Flèche indiquant la direction
        longueur = 30

        pointe_x = ecran_x + longueur * math.cos(angle_h)
        pointe_y = ecran_y + longueur * math.sin(angle_h)

        self.canvas.create_line(
            ecran_x, ecran_y,
            pointe_x, pointe_y,
            fill=self.BLANC,
            width=4,
            arrow=tk.LAST
        )

        self.canvas.create_text(
            ecran_x,
            ecran_y - 35,
            text="ROBOT",
            fill=self.BLANC,
            font=("Arial", 10, "bold")
        )

    # ==========================================
    # MISE A JOUR DES INFORMATIONS
    # ==========================================

    def mettre_a_jour_informations(self):

        x, y, z = self.robot.obtenir_position()

        self.label_position.config(
            text=f"Position : X={x:.1f}  Y={y:.1f}  Z={z:.1f}"
        )

        self.label_direction.config(
            text=(
                f"Direction : {self.robot.angle:.1f}° "
                f"| Inclinaison : {self.robot.angle_vertical:.1f}°"
            )
        )

        distance = self.capteur.mesurer_distance(
            self.robot,
            self.simulation.obtenir_obstacles(),
            self.simulation.largeur,
            self.simulation.hauteur,
            self.simulation.profondeur
        )

        etat = self.capteur.detecter_obstacle(distance)

        if etat == "DANGER":
            couleur = self.ROUGE
        elif etat == "ATTENTION":
            couleur = self.ORANGE
        else:
            couleur = self.VERT

        self.label_capteur.config(
            text=f"Capteur : {etat} ({distance:.1f})",
            fg=couleur
        )

    # ==========================================
    # COMMANDES MANUELLES
    # ==========================================

    def commander(self, action):

        self.arreter_automatique()
        self.robot.reprendre()

        x, y, z = self.robot.obtenir_position()

        if action == "AVANCER":
            nouvelle_position = self.robot.avancer()

        elif action == "RECULER":
            nouvelle_position = self.robot.reculer()

        elif action == "GAUCHE":
            self.robot.tourner_gauche()
            self.afficher_statut("Rotation vers la gauche", self.CYAN)
            self.actualiser()
            return

        elif action == "DROITE":
            self.robot.tourner_droite()
            self.afficher_statut("Rotation vers la droite", self.CYAN)
            self.actualiser()
            return

        elif action == "MONTER":
            nouvelle_position = (x, y, z + self.robot.vitesse)

        elif action == "DESCENDRE":
            nouvelle_position = (x, y, z - self.robot.vitesse)

        elif action == "HAUT":
            self.robot.incliner_haut()
            self.afficher_statut("Inclinaison vers le haut", self.CYAN)
            self.actualiser()
            return

        elif action == "BAS":
            self.robot.incliner_bas()
            self.afficher_statut("Inclinaison vers le bas", self.CYAN)
            self.actualiser()
            return

        else:
            return

        nx, ny, nz = nouvelle_position

        if self.simulation.verifier_collision(
            self.robot, nx, ny, nz
        ):
            self.afficher_statut(
                "Déplacement impossible : obstacle ou limite !",
                self.ROUGE
            )
        else:
            self.robot.definir_position(nx, ny, nz)
            self.afficher_statut(
                "Déplacement effectué",
                self.VERT
            )

        self.actualiser()

    # ==========================================
    # MODE AUTOMATIQUE
    # ==========================================

    def activer_automatique(self):

        try:
            destination_x = float(self.entree_x.get())
            destination_y = float(self.entree_y.get())
            destination_z = float(self.entree_z.get())

        except ValueError:
            self.afficher_statut(
                "Veuillez saisir des coordonnées numériques.",
                self.ROUGE
            )
            return

        if not (
            0 <= destination_x <= self.simulation.largeur
            and 0 <= destination_y <= self.simulation.hauteur
            and 0 <= destination_z <= self.simulation.profondeur
        ):
            self.afficher_statut(
                "La destination dépasse les limites de l'environnement.",
                self.ROUGE
            )
            return

        self.robot.reprendre()

        self.automatique.definir_destination(
            destination_x,
            destination_y,
            destination_z
        )

        self.automatique.activer()

        if not self.automatique.actif:
            self.afficher_statut(
                "Impossible d'activer le mode automatique.",
                self.ROUGE
            )
            return

        self.auto_en_cours = True
        self.bouton_auto.config(text="AUTOMATIQUE EN COURS")
        self.afficher_statut(
            "Le robot se dirige vers sa destination.",
            self.VERT
        )

        self.boucle_automatique()

    def boucle_automatique(self):

        if not self.auto_en_cours:
            return

        if not self.automatique.actif:
            self.arreter_automatique()
            self.afficher_statut(
                "Mode automatique terminé.",
                self.VERT
            )
            self.actualiser()
            return

        decision = self.automatique.executer_decision()

        if decision == "DESTINATION_ATTEINTE":
            self.arreter_automatique()
            self.afficher_statut(
                "Destination atteinte !",
                self.VERT
            )
            self.actualiser()
            return

        elif decision == "OBSTACLE":
            self.afficher_statut(
                "Obstacle détecté : recherche d'un passage.",
                self.ORANGE
            )

        else:
            self.afficher_statut(
                f"Mode automatique : {decision}",
                self.VERT
            )

        self.actualiser()

        self.identifiant_boucle = self.fenetre.after(
            200,
            self.boucle_automatique
        )

    def arreter_automatique(self):

        self.auto_en_cours = False

        if self.identifiant_boucle is not None:
            self.fenetre.after_cancel(self.identifiant_boucle)
            self.identifiant_boucle = None

        self.bouton_auto.config(text="MODE AUTOMATIQUE")

    # ==========================================
    # ARRET D'URGENCE
    # ==========================================

    def arreter(self):

        self.arreter_automatique()
        self.robot.arreter()

        self.afficher_statut(
            "ARRÊT D'URGENCE ACTIVÉ",
            self.ROUGE
        )

        self.actualiser()

    # ==========================================
    # REINITIALISATION
    # ==========================================

    def reinitialiser(self):

        self.arreter_automatique()

        self.robot.reprendre()
        
        self.robot.definir_position(*self.position_initiale)
        self.robot.angle = -90
        self.robot.angle_vertical = 0

        self.afficher_statut(
            "Robot réinitialisé.",
            self.VERT
        )

        self.actualiser()

    # ==========================================
    # ACTUALISATION GENERALE
    # ==========================================

    def actualiser(self):

        self.dessiner_simulation()
        self.dessiner_robot()
        self.mettre_a_jour_informations()

    # ==========================================
    # MESSAGE DE STATUT
    # ==========================================

    def afficher_statut(self, message, couleur):

        self.label_statut.config(
            text=message,
            fg=couleur
        )

    # ==========================================
    # FENETRE DE CONFIGURATION
    # ==========================================

    def ouvrir_configuration(self):

        fenetre_config = tk.Toplevel(self.fenetre)
        fenetre_config.title("Configuration du scénario")
        fenetre_config.geometry("480x700")
        fenetre_config.minsize(480, 650)
        fenetre_config.configure(bg=self.FOND)

        titre = tk.Label(
            fenetre_config,
            text="CONFIGURATION DU SCÉNARIO",
            font=("Arial", 15, "bold"),
            bg=self.FOND,
            fg=self.CYAN
        )
        titre.pack(pady=15)

        tk.Label(
            fenetre_config,
            text="Cette fenêtre permettra de définir les coordonnées du robot, de l'obstacle et de la destination.",
            wraplength=350,
            bg=self.FOND,
            fg=self.BLANC
        ).pack(pady=10)
        
# POSITION INITIALE DU ROBOT

        tk.Label(
            fenetre_config,
            text="POSITION INITIALE DU ROBOT",
            font=("Arial", 11, "bold"),
            bg=self.FOND,
            fg=self.VERT
        ).pack(pady=8)

        cadre_robot = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_robot.pack(pady=5)

        self.config_robot_x = self.creer_champ(
            cadre_robot, "Robot X", str(self.robot.x), 0
        )

        self.config_robot_y = self.creer_champ(
            cadre_robot, "Robot Y", str(self.robot.y), 1
        )

        self.config_robot_z = self.creer_champ(
            cadre_robot, "Robot Z", str(self.robot.z), 2
        )

        # POSITION DE L'OBSTACLE

        tk.Label(
            fenetre_config,
            text="POSITION DE L'OBSTACLE",
            font=("Arial", 11, "bold"),
            bg=self.FOND,
            fg=self.ORANGE
        ).pack(pady=8)

        cadre_obstacle = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_obstacle.pack(pady=5)

        self.config_obstacle_x = self.creer_champ(
            cadre_obstacle, "Obstacle X", "450", 0
        )

        self.config_obstacle_y = self.creer_champ(
            cadre_obstacle, "Obstacle Y", "200", 1
        )

        self.config_obstacle_z = self.creer_champ(
            cadre_obstacle, "Obstacle Z", "40", 2
        )

        cadre_rayon = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_rayon.pack(pady=5)

        self.config_obstacle_rayon = self.creer_champ(
            cadre_rayon, "Rayon", "30", 0
        )

# POSITION DU DEUXIÈME OBSTACLE

        tk.Label(
            fenetre_config,
            text="POSITION DU DEUXIÈME OBSTACLE",
            font=("Arial", 11, "bold"),
            bg=self.FOND,
            fg=self.ORANGE
        ).pack(pady=8)

        cadre_obstacle2 = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_obstacle2.pack(pady=5)

        self.config_obstacle2_x = self.creer_champ(
            cadre_obstacle2, "Obstacle 2 X", "275", 0
        )

        self.config_obstacle2_y = self.creer_champ(
            cadre_obstacle2, "Obstacle 2 Y", "435", 1
        )

        self.config_obstacle2_z = self.creer_champ(
            cadre_obstacle2, "Obstacle 2 Z", "0", 2
        )

        cadre_rayon2 = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_rayon2.pack(pady=5)

        self.config_obstacle2_rayon = self.creer_champ(
            cadre_rayon2, "Rayon 2", "83", 0
        )

        # DESTINATION DU ROBOT

        tk.Label(
            fenetre_config,
            text="DESTINATION DU ROBOT",
            font=("Arial", 11, "bold"),
            bg=self.FOND,
            fg=self.CYAN
        ).pack(pady=8)

        cadre_destination = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_destination.pack(pady=5)

        self.config_destination_x = self.creer_champ(
            cadre_destination, "Destination X", "700", 0
        )

        self.config_destination_y = self.creer_champ(
            cadre_destination, "Destination Y", "300", 1
        )

        self.config_destination_z = self.creer_champ(
            cadre_destination, "Destination Z", "40", 2
        )

        # BOUTON POUR APPLIQUER LA CONFIGURATION

        self.creer_bouton(
            fenetre_config,
            "APPLIQUER LE SCÉNARIO",
            lambda: self.appliquer_configuration(fenetre_config),
            self.VERT
        )

    def appliquer_configuration(self, fenetre_config):

        try:
            # 1. Lire la position du robot
            robot_x = float(self.config_robot_x.get())
            robot_y = float(self.config_robot_y.get())
            robot_z = float(self.config_robot_z.get())

            # 2. Lire le premier obstacle
            obstacle_x = float(self.config_obstacle_x.get())
            obstacle_y = float(self.config_obstacle_y.get())
            obstacle_z = float(self.config_obstacle_z.get())
            obstacle_rayon = float(self.config_obstacle_rayon.get())

            # 3. Lire le deuxième obstacle
            obstacle2_x = float(self.config_obstacle2_x.get())
            obstacle2_y = float(self.config_obstacle2_y.get())
            obstacle2_z = float(self.config_obstacle2_z.get())
            obstacle2_rayon = float(self.config_obstacle2_rayon.get())

            # 4. Lire la destination
            destination_x = float(self.config_destination_x.get())
            destination_y = float(self.config_destination_y.get())
            destination_z = float(self.config_destination_z.get())

        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Tous les champs doivent contenir des nombres."
            )
            return

        # 5. Vérifier les rayons
        if obstacle_rayon <= 0 or obstacle2_rayon <= 0:
            messagebox.showerror(
                "Erreur",
                "Les rayons doivent être positifs."
            )
            return

        # 6. Vérifier les limites du robot et de la destination
        r = self.robot.rayon

        for x, y, z, nom in [
            (robot_x, robot_y, robot_z, "Robot"),
            (destination_x, destination_y, destination_z, "Destination")
        ]:
            if not (
                r <= x <= self.simulation.largeur - r
                and r <= y <= self.simulation.hauteur - r
                and r <= z <= self.simulation.profondeur - r
            ):
                messagebox.showerror(
                    "Erreur",
                    f"La position du {nom} dépasse les limites."
                )
                return

        # 7. Vérifier les limites des deux obstacles
        for x, y, z, nom in [
            (obstacle_x, obstacle_y, obstacle_z, "Obstacle O1"),
            (obstacle2_x, obstacle2_y, obstacle2_z, "Obstacle O2")
        ]:
            if not (
                0 <= x <= self.simulation.largeur
                and 0 <= y <= self.simulation.hauteur
                and 0 <= z <= self.simulation.profondeur
            ):
                messagebox.showerror(
                    "Erreur",
                    f"La position de {nom} est invalide."
                )
                return

        # 8. Créer les deux obstacles pour les vérifications
        from obstacle import Obstacle

        obstacles_test = [
            Obstacle(
                "O1", obstacle_x, obstacle_y,
                obstacle_z, obstacle_rayon
            ),
            Obstacle(
                "O2", obstacle2_x, obstacle2_y,
                obstacle2_z, obstacle2_rayon
            )
        ]

        # 9. Vérifier les collisions avec le robot et la destination
        for obstacle in obstacles_test:

            if obstacle.verifier_collision(
                robot_x, robot_y, robot_z, r
            ):
                messagebox.showerror(
                    "Erreur",
                    f"Le robot commence dans {obstacle.identifiant}."
                )
                return

            if obstacle.verifier_collision(
                destination_x, destination_y, destination_z, r
            ):
                messagebox.showerror(
                    "Erreur",
                    f"La destination se trouve dans {obstacle.identifiant}."
                )
                return

        # 10. Arrêter le déplacement automatique
        self.arreter_automatique()
        self.automatique.desactiver()

        # 11. Placer le robot
        self.robot.reprendre()
        self.robot.definir_position(
            robot_x, robot_y, robot_z
        )

        self.robot.angle = -90
        self.robot.angle_vertical = 0

        # 12. Remplacer les anciens obstacles
        self.simulation.obstacles = []

        # Ajouter O1
        self.simulation.ajouter_obstacle(
            "O1",
            obstacle_x,
            obstacle_y,
            obstacle_z,
            obstacle_rayon
        )

        # Ajouter O2
        self.simulation.ajouter_obstacle(
            "O2",
            obstacle2_x,
            obstacle2_y,
            obstacle2_z,
            obstacle2_rayon
        )

        # 13. Enregistrer la position initiale
        self.position_initiale = (
            robot_x,
            robot_y,
            robot_z
        )

        # 14. Mettre à jour la destination
        self.entree_x.delete(0, tk.END)
        self.entree_x.insert(0, str(destination_x))

        self.entree_y.delete(0, tk.END)
        self.entree_y.insert(0, str(destination_y))

        self.entree_z.delete(0, tk.END)
        self.entree_z.insert(0, str(destination_z))

        self.automatique.definir_destination(
            destination_x,
            destination_y,
            destination_z
        )

        # 15. Actualiser l'affichage
        self.actualiser()

        self.afficher_statut(
            "Nouveau scénario configuré avec succès.",
            self.VERT
        )

        messagebox.showinfo(
            "Configuration réussie",
            "Les deux obstacles ont été ajoutés."
        )

        fenetre_config.destroy()
   