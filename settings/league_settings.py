# Einstellungen für die Ligen, die im Spiel spielbar sind.

from race import Race
from league import League

from settings.track_settings import TrackCreator, STD_REQUIRED_LAPS
from settings.music_settings import BGM_DICT

# ------------- Erstellung der verschiedenen Ligen im Spiel --------------------------

LEAGUE_1_RACES = [
    Race( # 0: erste Stadtstrecke im Event Horizon Biome
        race_track_creator = TrackCreator.create_track_2023,
        floor_tex_path = "gfx/event_horizon_track1.png",
        bg_tex_path = "gfx/event_horizon_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time-attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 1: erste Stadtstrecke
        race_track_creator = TrackCreator.create_track_2023,
        floor_tex_path = "gfx/track_2023.png",
        bg_tex_path = "gfx/track_2023_bg_resized.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time-attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = True,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 2: zweite Stadtstrecke
        race_track_creator = TrackCreator.create_track_2023_II,
        floor_tex_path = "gfx/track_2023_II.png",
        bg_tex_path = "gfx/track_2023_bg_resized.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time-attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = True,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 3: zweite Event Horizon Strecke
        race_track_creator = TrackCreator.create_event_horizon_track2,
        floor_tex_path = "gfx/event_horizon_track2.png",
        bg_tex_path = "gfx/event_horizon_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 26.26,
        init_player_pos_y = -98.86,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 4: erste Stadtstrecke im Schnee-Biom
        race_track_creator = TrackCreator.create_track_2023,
        floor_tex_path = "gfx/track_2023_snow.png",
        bg_tex_path = "gfx/track_2023_snow_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time-attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 5: Wüstenstrecke
        race_track_creator = TrackCreator.create_monochrome_track,
        floor_tex_path = "gfx/desert_track1.png",
        bg_tex_path = "gfx/monochrome_track_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 6: monochrome Strecke
        race_track_creator = TrackCreator.create_monochrome_track,
        floor_tex_path = "gfx/monochrome_track.png",
        bg_tex_path = "gfx/monochrome_track_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = True,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 7: leere Ebene im Schwarzes-Loch-Biom
        race_track_creator = TrackCreator.create_monochrome_track,
        floor_tex_path = "gfx/black_hole_track1.png",
        bg_tex_path = "gfx/black_hole_track_bg.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    ),
    Race( # 8: Weltraum-Hangar-Strecke
        race_track_creator = TrackCreator.create_monochrome_track,
        floor_tex_path = "gfx/space_hangar_track1.png",
        bg_tex_path = "gfx/space_hangar_bg_no_deco.png",
        required_laps = STD_REQUIRED_LAPS,
        race_mode = "time_attack",
        init_player_pos_x = 25.55,
        init_player_pos_y = -119.78,
        init_player_angle = -111.565,
        is_foggy = False,
        music_track_path = BGM_DICT["price-cover"]
    )
]
LEAGUE_1 = League(LEAGUE_1_RACES)

# Spezielle Liga, die nicht gespielt werden soll,
# sondern als Streckenliste dient, aus der im Einzelrennen-Modus ausgewählt werden kann
SINGLE_MODE_RACES = LEAGUE_1_RACES 

# ---------------------------- Ende der Liga-Erstellung --------------------------

LEAGUES = [LEAGUE_1]