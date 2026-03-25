import arcade

class Sword(arcade.TextureAnimationSprite):
    """
    Cette classe représente l'épée du joueur.

    J'ai choisi d'hériter de TextureAnimationSprite parce que :
    - l'épée doit être affichée dans le jeu
    - elle a une position (center_x, center_y)
    - elle possède une animation (animation d'attaque)

    En héritant de cette classe, je peux facilement :
    - la dessiner
    - lui donner une animation
    - gérer ses collisions (avec les crystaux)
    """


    def __init__(self, ):

    def use(self):
        if self.active:
            return
        self.active=True
        self.timer=0
        self.current_frame=0
