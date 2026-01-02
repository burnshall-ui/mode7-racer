# Einstellungen für die Ligen, die im Spiel spielbar sind.

from race import Race
from league import League

from settings.track_settings import TrackCreator, STD_REQUIRED_LAPS
from settings.music_settings import BGM_DICT

# ------------- Erzeugung der verschiedenen Ligen im Spiel --------------------------

LEAGUE_1_RACES = [
    Race( # 0: Funktioniert1 - Erste selbst erstellte Strecke
        race_track_creator = TrackCreator.create_funktioniert1,
        floor_tex_path = "gfx/new_track.png",
        bg_tex_path = "gfx/track_2023_snow_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 77.88,
        init_player_pos_y = -136.75,
        init_player_angle = -1.50,
        is_foggy = False,
        music_track_path = BGM_DICT["skyline-hyperdrive"]
    ),
    Race( # 1: Event Horizon I
        race_track_creator = TrackCreator.create_event_horizon_track2,
        floor_tex_path = "gfx/event_horizon_track1.png",
        bg_tex_path = "gfx/event_horizon_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 27.73,
        init_player_pos_y = -119.20,
        init_player_angle = 1.60,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 2: Space 3 - Komplexe Strecke mit vielen Kurven
        race_track_creator = TrackCreator.create_track_space3,
        floor_tex_path = "gfx/track_space3.png",
        bg_tex_path = "gfx/event_horizon_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 15.50,
        init_player_pos_y = -151.16,
        init_player_angle = 1.60,
        is_foggy = False,
        music_track_path = BGM_DICT["space3"]
    )
]
LEAGUE_1 = League(LEAGUE_1_RACES)

# Spezielle Liga, die nicht zum Spielen gedacht ist,
# sondern als Track-Liste für die Auswahl im Einzelrennen dient.
SINGLE_MODE_RACES = LEAGUE_1_RACES 

# ---------------------------- Ende der Ligenerzeugung --------------------------

LEAGUES = [LEAGUE_1]