import tkinter as tk
import math
import time
from tkinter import messagebox

from obstacle import Obstacle


class InterfaceGraphique:

    def __init__(
        self, fenetre, robot, capteur, simulation, automatique, historique
    ):
        self.fenetre = fenetre
        self.robot = robot
        self.capteur = capteur
        self.simulation = simulation
        self.automatique = automatique
        self.historique = historique

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
        self.compteur_blocage = 0
        self.auto_interrompu = False
        self.trace = []
        self.trace_affichee = False
        self.position_initiale = (
            self.robot.x,
            self.robot.y,
            self.robot.z
        )

        # Fenêtres secondaires (historique et obstacles)
        self.fenetre_historique = None
        self.zone_historique = None
        self.label_resume_historique = None
        self.fenetre_obstacles = None
        self.liste_obstacles = None

        self.creer_interface()

        # Première position de l'historique
        self.enregistrer("Départ", forcer=True)

        # Actualiser après la création complète de la fenêtre
        self.fenetre.after(100, self.actualiser)
        self.fenetre.after(200, self.boucle_trace)

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

        # Barre d'état : tous les messages du système s'affichent ici
        self.label_statut = tk.Label(
            zone_simulation,
            text="Système prêt (v4)",
            bg=self.PANNEAU,
            fg=self.VERT,
            font=("Arial", 11, "bold"),
            anchor="w",
            justify="left",
            padx=10,
            pady=6
        )
        self.label_statut.pack(side="bottom", fill="x")
        self.label_statut.bind(
            "<Configure>",
            lambda evenement: self.label_statut.config(
                wraplength=max(evenement.width - 20, 100)
            )
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

        # Panneau de commandes avec barre de défilement
        self.conteneur_commandes = tk.Frame(
            contenu,
            bg=self.PANNEAU,
            width=290
        )
        self.conteneur_commandes.pack(side="right", fill="y")
        self.conteneur_commandes.pack_propagate(False)

        self.canvas_commandes = tk.Canvas(
            self.conteneur_commandes,
            bg=self.PANNEAU,
            highlightthickness=0,
            yscrollincrement=20
        )

        barre = tk.Scrollbar(
            self.conteneur_commandes,
            orient="vertical",
            command=self.canvas_commandes.yview,
            bg="#475569",
            troughcolor=self.PANNEAU,
            activebackground=self.CYAN,
            highlightthickness=0,
            bd=0,
            width=12
        )
        self.canvas_commandes.configure(yscrollcommand=barre.set)

        barre.pack(side="right", fill="y")
        self.canvas_commandes.pack(side="left", fill="both", expand=True)

        panneau = tk.Frame(self.canvas_commandes, bg=self.PANNEAU)
        fenetre_interne = self.canvas_commandes.create_window(
            (0, 0), window=panneau, anchor="nw"
        )

        panneau.bind(
            "<Configure>",
            lambda evenement: self.canvas_commandes.configure(
                scrollregion=self.canvas_commandes.bbox("all")
            )
        )
        self.canvas_commandes.bind(
            "<Configure>",
            lambda evenement: self.canvas_commandes.itemconfig(
                fenetre_interne, width=evenement.width
            )
        )

        # Défilement à la molette (Windows, macOS et Linux)
        self.fenetre.bind_all("<MouseWheel>", self.defiler_commandes)
        self.fenetre.bind_all("<Button-4>", self.defiler_commandes)
        self.fenetre.bind_all("<Button-5>", self.defiler_commandes)

        self.creer_commandes(panneau)

    def defiler_commandes(self, evenement):
        """Fait défiler le panneau si la souris est au-dessus."""

        try:
            widget = self.fenetre.winfo_containing(
                evenement.x_root, evenement.y_root
            )
        except (KeyError, tk.TclError):
            return

        while widget is not None:
            if widget == self.conteneur_commandes:
                break
            widget = widget.master
        else:
            return

        if evenement.num == 4:
            sens = -1
        elif evenement.num == 5:
            sens = 1
        else:
            sens = -1 if evenement.delta > 0 else 1

        self.canvas_commandes.yview_scroll(sens, "units")

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

        # La destination s'affiche sur la simulation pendant la saisie
        for entree in (self.entree_x, self.entree_y, self.entree_z):
            entree.bind(
                "<KeyRelease>",
                lambda evenement: self.actualiser()
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

        # Arrêt, reprise et réinitialisation
        self.creer_bouton(
            panneau, "ARRÊT D'URGENCE", self.arreter,
            self.ROUGE
        )

        self.creer_bouton(
            panneau, "REPRENDRE", self.reprendre,
            self.VERT
        )

        self.creer_bouton(
            panneau, "RÉINITIALISER", self.reinitialiser,
            "#475569"
        )

        # Historique et obstacles
        self.creer_bouton(
            panneau, "HISTORIQUE DES DÉPLACEMENTS", self.ouvrir_historique,
            self.CYAN
        )

        self.creer_bouton(
            panneau, "GÉRER LES OBSTACLES", self.ouvrir_obstacles,
            self.ORANGE
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

        self.label_distance = tk.Label(
            panneau,
            text="Distance parcourue : 0.0",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 10)
        )
        self.label_distance.pack(pady=4)

        self.label_nb_positions = tk.Label(
            panneau,
            text="Positions enregistrées : 0",
            bg=self.PANNEAU,
            fg=self.BLANC,
            font=("Arial", 10)
        )
        self.label_nb_positions.pack(pady=4)

        self.label_etat = tk.Label(
            panneau,
            text="Robot : ACTIF",
            bg=self.PANNEAU,
            fg=self.VERT,
            font=("Arial", 10, "bold")
        )
        self.label_etat.pack(pady=4)

        self.label_capteur = tk.Label(
            panneau,
            text="Capteur : LIBRE",
            bg=self.PANNEAU,
            fg=self.VERT,
            font=("Arial", 10, "bold")
        )
        self.label_capteur.pack(pady=4)

        tk.Frame(panneau, bg=self.PANNEAU, height=12).pack()

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
    # OUTILS
    # ==========================================

    def formater(self, valeur):
        """Affiche 450 au lieu de 450.0."""

        valeur = float(valeur)

        if valeur.is_integer():
            return str(int(valeur))

        return str(round(valeur, 2))

    def lire_destination(self):
        """Retourne (x, y, z) si les champs sont valides, sinon None."""

        if not hasattr(self, "entree_z"):
            return None

        try:
            return (
                float(self.entree_x.get()),
                float(self.entree_y.get()),
                float(self.entree_z.get())
            )
        except ValueError:
            return None

    def enregistrer(self, action, forcer=False):
        """Enregistre la position actuelle du robot dans l'historique."""

        x, y, z = self.robot.obtenir_position()

        ajoutee = self.historique.enregistrer_position(
            x, y, z, action, forcer
        )

        if forcer:
            # Départ, réinitialisation, nouveau scénario : trait effacé
            self.trace = [(x, y, z, time.time())]
        elif ajoutee:
            self.trace.append((x, y, z, time.time()))

        self.rafraichir_historique()

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
    # DESSIN DE LA DESTINATION ET DU TRAJET
    # ==========================================

    def dessiner_destination(self):

        destination = self.lire_destination()

        if destination is None:
            return

        x, y, z = destination

        ecran_x, ecran_y = self.projeter(x, y, z)
        sol_x, sol_y = self.projeter(x, y, 0)

        # Liaison verticale avec le sol
        self.canvas.create_line(
            sol_x, sol_y,
            ecran_x, ecran_y,
            fill=self.ORANGE,
            dash=(3, 3)
        )

        # Losange de destination
        t = 9

        self.canvas.create_polygon(
            ecran_x, ecran_y - t,
            ecran_x + t, ecran_y,
            ecran_x, ecran_y + t,
            ecran_x - t, ecran_y,
            fill=self.ORANGE,
            outline=self.BLANC,
            width=2
        )

        self.canvas.create_text(
            ecran_x,
            ecran_y - t - 10,
            text="DESTINATION",
            fill=self.ORANGE,
            font=("Arial", 9, "bold")
        )

    # Durée (en secondes) pendant laquelle le trait reste visible
    DUREE_TRACE = 3.0

    def melanger_couleur(self, depart, arrivee, t):
        """Couleur intermédiaire entre deux couleurs #RRGGBB."""

        c1 = [int(depart[i:i + 2], 16) for i in (1, 3, 5)]
        c2 = [int(arrivee[i:i + 2], 16) for i in (1, 3, 5)]

        return "#%02X%02X%02X" % tuple(
            int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)
        )

    def dessiner_trajet(self):
        """Trait derrière le robot : il s'estompe avec le temps."""

        maintenant = time.time()

        # Oublier les anciens points (on garde toujours le dernier)
        self.trace = [
            point for point in self.trace[:-1]
            if maintenant - point[3] < self.DUREE_TRACE
        ] + self.trace[-1:]

        for i in range(1, len(self.trace)):
            x1, y1, z1, _ = self.trace[i - 1]
            x2, y2, z2, instant = self.trace[i]

            age = maintenant - instant

            if age >= self.DUREE_TRACE:
                continue

            # Plus le segment est ancien, plus il est sombre
            force = 1 - age / self.DUREE_TRACE
            couleur = self.melanger_couleur(
                "#111827", self.CYAN, 0.1 + 0.9 * force
            )

            ecran_x1, ecran_y1 = self.projeter(x1, y1, z1)
            ecran_x2, ecran_y2 = self.projeter(x2, y2, z2)

            self.canvas.create_line(
                ecran_x1, ecran_y1, ecran_x2, ecran_y2,
                fill=couleur,
                width=2
            )

    def boucle_trace(self):
        """Redessine régulièrement tant que le trait s'estompe."""

        visible = (
            len(self.trace) >= 2
            and time.time() - self.trace[-1][3] < self.DUREE_TRACE
        )

        if visible or self.trace_affichee:
            self.actualiser()

        self.trace_affichee = visible
        self.fenetre.after(100, self.boucle_trace)

    def dessiner_trajectoire_prevue(self):
        """Chemin calculé par A* devant le robot (pointillés blancs)."""

        if not self.auto_en_cours or not self.automatique.trajectoire:
            return

        points = [self.robot.obtenir_position()]
        points.extend(self.automatique.trajectoire)

        coordonnees = []

        for x, y, z in points:
            coordonnees.extend(self.projeter(x, y, z))

        self.canvas.create_line(
            *coordonnees,
            fill=self.BLANC,
            width=2,
            dash=(2, 5)
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

        self.label_distance.config(
            text=(
                f"Distance parcourue : "
                f"{self.historique.calculer_distance():.1f}"
            )
        )

        self.label_nb_positions.config(
            text=(
                f"Positions enregistrées : "
                f"{self.historique.nombre_positions()}"
            )
        )

        if self.robot.actif:
            self.label_etat.config(text="Robot : ACTIF", fg=self.VERT)
        else:
            self.label_etat.config(text="Robot : ARRÊTÉ", fg=self.ROUGE)

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

        if not self.robot.actif:
            self.afficher_statut(
                "Robot à l'arrêt : appuyez sur REPRENDRE.",
                self.ROUGE
            )
            self.actualiser()
            return

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
            self.enregistrer(action.capitalize())
            self.afficher_statut(
                "Déplacement effectué",
                self.VERT
            )

        self.actualiser()

    # ==========================================
    # MODE AUTOMATIQUE
    # ==========================================

    def activer_automatique(self, reprise=False):

        if not self.robot.actif:
            self.afficher_statut(
                "Robot à l'arrêt : appuyez sur REPRENDRE.",
                self.ROUGE
            )
            return

        destination = self.lire_destination()

        if destination is None:
            self.afficher_statut(
                "Veuillez saisir des coordonnées numériques.",
                self.ROUGE
            )
            return

        destination_x, destination_y, destination_z = destination
        r = self.robot.rayon

        largeur = self.simulation.largeur
        hauteur = self.simulation.hauteur
        profondeur = self.simulation.profondeur

        # Hors de l'environnement : refusé
        if not (
            0 <= destination_x <= largeur
            and 0 <= destination_y <= hauteur
            and 0 <= destination_z <= profondeur
        ):
            message = (
                f"Destination hors de l'environnement. "
                f"X : 0 à {largeur}, Y : 0 à {hauteur}, "
                f"Z : 0 à {profondeur}."
            )
            self.afficher_statut(message, self.ROUGE)
            messagebox.showwarning("Destination invalide", message)
            return

        # Trop près d'un bord : le robot ira au plus près
        ajustee = (
            min(max(destination_x, r), largeur - r),
            min(max(destination_y, r), hauteur - r),
            min(max(destination_z, r), profondeur - r)
        )

        if ajustee != (destination_x, destination_y, destination_z):
            destination_x, destination_y, destination_z = ajustee

            for entree, valeur in (
                (self.entree_x, destination_x),
                (self.entree_y, destination_y),
                (self.entree_z, destination_z)
            ):
                entree.delete(0, tk.END)
                entree.insert(0, self.formater(valeur))

            messagebox.showinfo(
                "Destination ajustée",
                f"Le robot a un rayon de {r:g} et ne peut pas toucher "
                f"les bords. Destination ajustée à "
                f"X={self.formater(destination_x)}, "
                f"Y={self.formater(destination_y)}, "
                f"Z={self.formater(destination_z)}."
            )

        for obstacle in self.simulation.obtenir_obstacles():
            if obstacle.verifier_collision(
                destination_x, destination_y, destination_z, r
            ):
                self.afficher_statut(
                    f"La destination se trouve dans {obstacle.identifiant}.",
                    self.ROUGE
                )
                return

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
        self.auto_interrompu = False
        self.compteur_blocage = 0

        # Nouveau trajet : le trait repart de la position actuelle
        if not reprise:
            x, y, z = self.robot.obtenir_position()
            self.trace = [(x, y, z, time.time())]
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
            self.compteur_blocage += 1

            # Le robot est bloqué depuis trop longtemps
            if self.compteur_blocage >= 3:
                self.arreter_automatique()
                self.afficher_statut(
                    "Robot bloqué : aucun passage vers la destination.",
                    self.ROUGE
                )
                self.actualiser()
                return

            self.afficher_statut(
                "Obstacle détecté : recherche d'un passage.",
                self.ORANGE
            )

        else:
            self.compteur_blocage = 0
            self.enregistrer("Automatique")
            if decision == "EVITER":
                self.afficher_statut(
                    "Obstacle détecté : le robot contourne l'obstacle.",
                    self.ORANGE
                )
            else:
                self.afficher_statut(
                    "Le robot avance vers sa destination.",
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

        self.automatique.desactiver()
        self.bouton_auto.config(text="MODE AUTOMATIQUE")

    # ==========================================
    # ARRET D'URGENCE ET REPRISE
    # ==========================================

    def arreter(self):

        # On retient si le mode automatique était en cours
        self.auto_interrompu = self.auto_en_cours

        self.arreter_automatique()
        self.robot.arreter()

        self.afficher_statut(
            "ARRÊT D'URGENCE ACTIVÉ",
            self.ROUGE
        )

        self.actualiser()

    def reprendre(self):

        self.robot.reprendre()

        # Si le robot allait vers sa destination, il repart
        if self.auto_interrompu:
            self.auto_interrompu = False
            self.activer_automatique(reprise=True)
            return

        self.afficher_statut(
            "Robot repris : prêt à recevoir des commandes.",
            self.VERT
        )

        self.actualiser()

    # ==========================================
    # REINITIALISATION
    # ==========================================

    def reinitialiser(self):

        self.arreter_automatique()
        self.auto_interrompu = False

        self.robot.reprendre()

        self.robot.definir_position(*self.position_initiale)
        self.robot.angle = -90
        self.robot.angle_vertical = 0

        self.historique.reinitialiser()
        self.enregistrer("Réinitialisation", forcer=True)

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
        self.dessiner_destination()
        self.dessiner_trajet()
        self.dessiner_trajectoire_prevue()
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
    # FENETRE D'HISTORIQUE
    # ==========================================

    def ouvrir_historique(self):

        if (
            self.fenetre_historique is not None
            and self.fenetre_historique.winfo_exists()
        ):
            self.fenetre_historique.lift()
            self.rafraichir_historique()
            return

        fen = tk.Toplevel(self.fenetre)
        fen.title("Historique des déplacements")
        fen.geometry("620x480")
        fen.minsize(560, 360)
        fen.configure(bg=self.FOND)

        self.fenetre_historique = fen

        tk.Label(
            fen,
            text="HISTORIQUE DES DÉPLACEMENTS",
            font=("Arial", 15, "bold"),
            bg=self.FOND,
            fg=self.CYAN
        ).pack(pady=12)

        self.label_resume_historique = tk.Label(
            fen,
            text="",
            font=("Arial", 10, "bold"),
            bg=self.FOND,
            fg=self.BLANC
        )
        self.label_resume_historique.pack(pady=(0, 8))

        cadre_texte = tk.Frame(fen, bg=self.PANNEAU)
        cadre_texte.pack(fill="both", expand=True, padx=15, pady=5)

        barre = tk.Scrollbar(
            cadre_texte,
            orient="vertical",
            bg="#475569",
            troughcolor=self.PANNEAU,
            activebackground=self.CYAN,
            highlightthickness=0,
            bd=0,
            width=12
        )
        barre.pack(side="right", fill="y")

        self.zone_historique = tk.Text(
            cadre_texte,
            bg="#111827",
            fg=self.BLANC,
            font=("Courier", 10),
            relief="flat",
            wrap="none",
            state="disabled",
            yscrollcommand=barre.set
        )
        self.zone_historique.pack(side="left", fill="both", expand=True)
        barre.config(command=self.zone_historique.yview)

        self.creer_bouton(
            fen, "EFFACER L'HISTORIQUE", self.effacer_historique,
            self.ORANGE
        )
        self.creer_bouton(
            fen, "FERMER", fen.destroy,
            "#475569"
        )

        self.rafraichir_historique()

    def rafraichir_historique(self):

        fen = self.fenetre_historique

        if fen is None or not fen.winfo_exists():
            return

        lignes = self.historique.afficher_parcours()

        self.zone_historique.config(state="normal")
        self.zone_historique.delete("1.0", tk.END)
        self.zone_historique.insert(tk.END, "\n".join(lignes))
        self.zone_historique.config(state="disabled")
        self.zone_historique.see(tk.END)

        self.label_resume_historique.config(
            text=(
                f"{self.historique.nombre_positions()} positions  |  "
                f"Distance totale : "
                f"{self.historique.calculer_distance():.1f}"
            )
        )

    def effacer_historique(self):

        self.historique.reinitialiser()
        self.enregistrer("Départ", forcer=True)
        self.afficher_statut("Historique effacé.", self.ORANGE)
        self.actualiser()

    # ==========================================
    # FENETRE DE GESTION DES OBSTACLES
    # ==========================================

    def ouvrir_obstacles(self):

        if (
            self.fenetre_obstacles is not None
            and self.fenetre_obstacles.winfo_exists()
        ):
            self.fenetre_obstacles.lift()
            self.rafraichir_liste_obstacles()
            return

        fen = tk.Toplevel(self.fenetre)
        fen.title("Gestion des obstacles")
        fen.geometry("480x600")
        fen.minsize(480, 560)
        fen.configure(bg=self.FOND)

        self.fenetre_obstacles = fen

        tk.Label(
            fen,
            text="GESTION DES OBSTACLES",
            font=("Arial", 15, "bold"),
            bg=self.FOND,
            fg=self.CYAN
        ).pack(pady=12)

        self.liste_obstacles = tk.Listbox(
            fen,
            height=7,
            bg="#111827",
            fg=self.BLANC,
            selectbackground=self.ORANGE,
            selectforeground="#FFFFFF",
            font=("Courier", 10),
            relief="flat",
            highlightthickness=0,
            exportselection=False
        )
        self.liste_obstacles.pack(fill="x", padx=15, pady=5)

        self.creer_bouton(
            fen, "SUPPRIMER L'OBSTACLE SÉLECTIONNÉ",
            self.supprimer_obstacle_interface,
            self.ROUGE
        )

        tk.Label(
            fen,
            text="NOUVEL OBSTACLE",
            font=("Arial", 11, "bold"),
            bg=self.FOND,
            fg=self.ORANGE
        ).pack(pady=(15, 5))

        cadre_position = tk.Frame(fen, bg=self.FOND)
        cadre_position.pack(pady=5)

        self.nouvel_obstacle_x = self.creer_champ(
            cadre_position, "X", "400", 0
        )
        self.nouvel_obstacle_y = self.creer_champ(
            cadre_position, "Y", "300", 1
        )
        self.nouvel_obstacle_z = self.creer_champ(
            cadre_position, "Z", "0", 2
        )
        self.nouvel_obstacle_rayon = self.creer_champ(
            cadre_position, "Rayon", "50", 3
        )

        self.creer_bouton(
            fen, "AJOUTER L'OBSTACLE",
            self.ajouter_obstacle_interface,
            self.VERT
        )
        self.creer_bouton(
            fen, "FERMER", fen.destroy,
            "#475569"
        )

        self.rafraichir_liste_obstacles()

    def rafraichir_liste_obstacles(self):

        fen = self.fenetre_obstacles

        if fen is None or not fen.winfo_exists():
            return

        self.liste_obstacles.delete(0, tk.END)

        for obstacle in self.simulation.obtenir_obstacles():
            self.liste_obstacles.insert(
                tk.END,
                f"{obstacle.identifiant:<4} "
                f"X={self.formater(obstacle.x)} "
                f"Y={self.formater(obstacle.y)} "
                f"Z={self.formater(obstacle.z)} "
                f"R={self.formater(obstacle.rayon)}"
            )

    def nouvel_identifiant(self):
        """Premier identifiant libre : O1, O2, O3..."""

        utilises = {
            obstacle.identifiant
            for obstacle in self.simulation.obtenir_obstacles()
        }

        numero = 1

        while f"O{numero}" in utilises:
            numero += 1

        return f"O{numero}"

    def ajouter_obstacle_interface(self):

        fen = self.fenetre_obstacles

        try:
            x = float(self.nouvel_obstacle_x.get())
            y = float(self.nouvel_obstacle_y.get())
            z = float(self.nouvel_obstacle_z.get())
            rayon = float(self.nouvel_obstacle_rayon.get())

        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Tous les champs doivent contenir des nombres.",
                parent=fen
            )
            return

        identifiant = self.nouvel_identifiant()
        r = self.robot.rayon

        test = Obstacle(identifiant, x, y, z, rayon)

        if test.verifier_collision(*self.robot.obtenir_position(), r):
            messagebox.showerror(
                "Erreur",
                "Le robot se trouve dans cette zone.",
                parent=fen
            )
            return

        destination = self.lire_destination()

        if destination is not None and test.verifier_collision(
            *destination, r
        ):
            messagebox.showerror(
                "Erreur",
                "La destination se trouve dans cette zone.",
                parent=fen
            )
            return

        try:
            self.simulation.ajouter_obstacle(
                identifiant, x, y, z, rayon
            )
        except ValueError as erreur:
            messagebox.showerror("Erreur", str(erreur), parent=fen)
            return

        self.afficher_statut(
            f"Obstacle {identifiant} ajouté.",
            self.VERT
        )
        self.rafraichir_liste_obstacles()
        self.actualiser()

    def supprimer_obstacle_interface(self):

        selection = self.liste_obstacles.curselection()

        if not selection:
            messagebox.showinfo(
                "Information",
                "Sélectionnez d'abord un obstacle dans la liste.",
                parent=self.fenetre_obstacles
            )
            return

        obstacles = self.simulation.obtenir_obstacles()
        identifiant = obstacles[selection[0]].identifiant

        self.simulation.supprimer_obstacle(identifiant)

        self.afficher_statut(
            f"Obstacle {identifiant} supprimé.",
            self.ORANGE
        )
        self.rafraichir_liste_obstacles()
        self.actualiser()

    # ==========================================
    # FENETRE DE CONFIGURATION
    # ==========================================

    def valeurs_obstacle(self, identifiant, defaut):
        """Valeurs actuelles de l'obstacle (x, y, z, rayon) en texte."""

        for obstacle in self.simulation.obtenir_obstacles():
            if obstacle.identifiant == identifiant:
                return tuple(
                    self.formater(valeur)
                    for valeur in (
                        obstacle.x, obstacle.y, obstacle.z, obstacle.rayon
                    )
                )

        return defaut

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
            text=(
                "Définissez le robot, les obstacles O1 et O2 et la "
                "destination. Appliquer remplace les obstacles actuels."
            ),
            wraplength=400,
            bg=self.FOND,
            fg=self.BLANC
        ).pack(pady=5)

        o1 = self.valeurs_obstacle("O1", ("450", "200", "0", "71"))
        o2 = self.valeurs_obstacle("O2", ("275", "435", "0", "83"))

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
            cadre_robot, "Robot X",
            self.formater(self.position_initiale[0]), 0
        )

        self.config_robot_y = self.creer_champ(
            cadre_robot, "Robot Y",
            self.formater(self.position_initiale[1]), 1
        )

        self.config_robot_z = self.creer_champ(
            cadre_robot, "Robot Z",
            self.formater(self.position_initiale[2]), 2
        )

        # POSITION DE L'OBSTACLE

        tk.Label(
            fenetre_config,
            text="POSITION DE L'OBSTACLE O1",
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
            cadre_obstacle, "Obstacle X", o1[0], 0
        )

        self.config_obstacle_y = self.creer_champ(
            cadre_obstacle, "Obstacle Y", o1[1], 1
        )

        self.config_obstacle_z = self.creer_champ(
            cadre_obstacle, "Obstacle Z", o1[2], 2
        )

        cadre_rayon = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_rayon.pack(pady=5)

        self.config_obstacle_rayon = self.creer_champ(
            cadre_rayon, "Rayon", o1[3], 0
        )

        # POSITION DU DEUXIÈME OBSTACLE

        tk.Label(
            fenetre_config,
            text="POSITION DU DEUXIÈME OBSTACLE O2",
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
            cadre_obstacle2, "Obstacle 2 X", o2[0], 0
        )

        self.config_obstacle2_y = self.creer_champ(
            cadre_obstacle2, "Obstacle 2 Y", o2[1], 1
        )

        self.config_obstacle2_z = self.creer_champ(
            cadre_obstacle2, "Obstacle 2 Z", o2[2], 2
        )

        cadre_rayon2 = tk.Frame(
            fenetre_config,
            bg=self.FOND
        )
        cadre_rayon2.pack(pady=5)

        self.config_obstacle2_rayon = self.creer_champ(
            cadre_rayon2, "Rayon 2", o2[3], 0
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
            cadre_destination, "Destination X", self.entree_x.get(), 0
        )

        self.config_destination_y = self.creer_champ(
            cadre_destination, "Destination Y", self.entree_y.get(), 1
        )

        self.config_destination_z = self.creer_champ(
            cadre_destination, "Destination Z", self.entree_z.get(), 2
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
                "Tous les champs doivent contenir des nombres.",
                parent=fenetre_config
            )
            return

        # La destination est ramenée à la zone atteignable par le robot
        rayon_robot = self.robot.rayon

        if not (
            0 <= destination_x <= self.simulation.largeur
            and 0 <= destination_y <= self.simulation.hauteur
            and 0 <= destination_z <= self.simulation.profondeur
        ):
            messagebox.showerror(
                "Erreur",
                "La destination est hors de l'environnement.",
                parent=fenetre_config
            )
            return

        destination_x = min(
            max(destination_x, rayon_robot),
            self.simulation.largeur - rayon_robot
        )
        destination_y = min(
            max(destination_y, rayon_robot),
            self.simulation.hauteur - rayon_robot
        )
        destination_z = min(
            max(destination_z, rayon_robot),
            self.simulation.profondeur - rayon_robot
        )

        # 5. Vérifier les rayons
        if obstacle_rayon <= 0 or obstacle2_rayon <= 0:
            messagebox.showerror(
                "Erreur",
                "Les rayons doivent être positifs.",
                parent=fenetre_config
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
                    f"La position du {nom} dépasse les limites.",
                    parent=fenetre_config
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
                    f"La position de {nom} est invalide.",
                    parent=fenetre_config
                )
                return

        # 8. Créer les deux obstacles pour les vérifications
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
                    f"Le robot commence dans {obstacle.identifiant}.",
                    parent=fenetre_config
                )
                return

            if obstacle.verifier_collision(
                destination_x, destination_y, destination_z, r
            ):
                messagebox.showerror(
                    "Erreur",
                    f"La destination se trouve dans {obstacle.identifiant}.",
                    parent=fenetre_config
                )
                return

        # 10. Arrêter le déplacement automatique
        self.arreter_automatique()
        self.auto_interrompu = False

        # 11. Placer le robot
        self.robot.reprendre()
        self.robot.definir_position(
            robot_x, robot_y, robot_z
        )

        self.robot.angle = -90
        self.robot.angle_vertical = 0

        # 12. Remplacer les anciens obstacles
        self.simulation.obstacles = []

        self.simulation.ajouter_obstacle(
            "O1",
            obstacle_x,
            obstacle_y,
            obstacle_z,
            obstacle_rayon
        )

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
        self.entree_x.insert(0, self.formater(destination_x))

        self.entree_y.delete(0, tk.END)
        self.entree_y.insert(0, self.formater(destination_y))

        self.entree_z.delete(0, tk.END)
        self.entree_z.insert(0, self.formater(destination_z))

        self.automatique.definir_destination(
            destination_x,
            destination_y,
            destination_z
        )

        # 15. Nouvel historique pour le nouveau scénario
        self.historique.reinitialiser()
        self.enregistrer("Nouveau scénario", forcer=True)
        self.rafraichir_liste_obstacles()

        # 16. Actualiser l'affichage
        self.actualiser()

        self.afficher_statut(
            "Nouveau scénario configuré avec succès.",
            self.VERT
        )

        messagebox.showinfo(
            "Configuration réussie",
            "Les deux obstacles ont été ajoutés.",
            parent=fenetre_config
        )

        fenetre_config.destroy()