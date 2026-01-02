# Dieses Modul baut eine Animations-Graph-ähnliche API auf,
# die verwendet werden kann, um zwischen den mehreren Animationen
# eines animierten Objekts im Spiel zu spielen und zu wechseln.



# Eine Klasse, die eine Frame-basierte Animation modelliert,
# bestehend aus einer Liste von Frames sowie einer Wiedergabegeschwindigkeit für die Animation.
#
# Verfolgt auch den Frame der Animation, der derzeit angezeigt wird.
# 
# Um unterschiedliche Animationsgeschwindigkeiten zu ermöglichen,
# ist die Frame-Position eine Gleitkommazahl (anstatt einer Ganzzahl, wie man erwarten könnte).
# Die aktuelle Framenummer ist der ganzzahlige Teil der frame_position-Variable,
# während der Bruchteil davon den Prozentsatz der Dauer des aktuellen Frames quantifiziert, der bereits vergangen ist
# (Dank an den YouTuber Clear Code für die Idee mit der gebrochenen Frame-Position, um unterschiedliche Animations-Wiedergabegeschwindigkeiten zu ermöglichen).
class Animation:
    def __init__(self, frames, speed):
        self.frames = frames # Liste der Frames, aus denen die Animation besteht (Inhalte haben Typ pygame.Surface)
        self.speed = speed # Parameter, der verwendet wird, um zu steuern, wie schnell die Animation abgespielt wird
        self.frame_position = 0.0 # zeigt die aktuelle Position in der Animation an

    # Gibt die Länge der Animation in Frames zurück.
    def length(self):
        return len(self.frames)

    # Startet die Animation neu, indem zum ersten Frame gesprungen wird.
    def restart(self):
        self.frame_position = 0.0

    # Bewegt diese Animation um einen Betrag vor, der proportional zum übergebenen Delta ist.
    # Das Delta ist die Zeit seit dem aktuellen Frame des Spiels (nicht der Animation!)
    # und dem letzten Frame des Spiels.
    # Dies macht die Animations-Wiedergabegeschwindigkeit unabhängig von der Framerate
    # der Hardware, die das Spiel derzeit ausführt.
    def advance(self, delta):
        self.frame_position += delta * self.speed

        # bei Überlauf umwickeln
        while self.frame_position > self.length():
            self.frame_position -= self.length()

    # Gibt den aktuellen Frame dieser Animation zurück.
    def current_frame(self):
        # Ganzzahl-Typumwandlung schneidet den Bruchteil ab, effektiv Abrunden der Zahl
        return self.frames[int(self.frame_position) % self.length()]



# Eine Klasse, die ein animiertes Objekt mit seinen verschiedenen Animationen repräsentiert.
# Verfolgt auch, welche Animation derzeit abgespielt wird.
#
# Animationen werden in einem Wörterbuch mit Strings als Schlüssel gespeichert.
class AnimatedObject:
    def __init__(self, animations):
        self.animations = animations # Wörterbuch, das die Animationen enthält
        self.current_anim = None # aktuelle Animation (Objektvariable wird erstellt, kann aber nicht sinnvoll initialisiert werden)
    
    # Wechselt zur Animation, die durch den übergebenen Schlüssel (String) identifiziert wird.
    def switch_animation(self, new_anim_key):
        # tatsächliches Wechseln
        self.current_anim = self.animations[new_anim_key]

        # Animation neu starten, um einen wohldefinierten Start/Übergang zu haben
        self.current_anim.restart()

    # Gibt den aktuellen Frame der aktuellen Animation zurück.
    def current_frame(self):
        return self.current_anim.current_frame()
    
    # Bewegt die aktuelle Animation um einen Betrag vor, der proportional zum übergebenen Delta ist.
    # 
    # Parameter:
    # delta - Zeit zwischen dem letzten gerenderten Spiel-Frame und dem aktuellen
    def advance_current_animation(self, delta):
        self.current_anim.advance(delta)



# Eine Klasse, die die Animationen für die Maschinen behandelt, die im Spiel steuerbar sind.
class AnimatedMachine(AnimatedObject):
    # Konstruktor, der den Animationsautomaten für die Maschine einrichtet.
    def __init__(self, driving_anim, idle_anim, jumping_anim):
        super().__init__({ "idle": idle_anim, "driving": driving_anim, "jumping": jumping_anim })

    def switch_to_driving_animation(self):
        self.switch_animation("driving")

    def switch_to_idle_animation(self):
        self.switch_animation("idle")

    def switch_to_jumping_animation(self):
        self.switch_animation("jumping")