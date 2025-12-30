# Settings for the leagues that are playable in the game.

from race import Race
from league import League

from settings.track_settings import TrackCreator, STD_REQUIRED_LAPS
from settings.music_settings import BGM_DICT

# ------------- creation of the different leagues in the game --------------------------

LEAGUE_1_RACES = [
    Race( # 0: Funktioniert1 - Erste selbst erstellte Strecke
        race_track_creator = TrackCreator.create_funktioniert1,
        floor_tex_path = "gfx/new_track.png",
        bg_tex_path = "gfx/event_horizon_bg.png",
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
    )
]
LEAGUE_1 = League(LEAGUE_1_RACES)

# special league that is not meant to be played
# but serves as the track list to select from in single race
SINGLE_MODE_RACES = LEAGUE_1_RACES 

# ---------------------------- end of league creation --------------------------

LEAGUES = [LEAGUE_1]