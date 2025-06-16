\
import json
import os

# Determine the project root directory (vult-1)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ASSET_BASE_PATH = os.path.join(PROJECT_ROOT, "src", "assets")
DATA_BASE_PATH = os.path.join(PROJECT_ROOT, "src", "data")

def _resolve_asset_path(relative_path):
    """Resolves a relative asset path to an absolute path."""
    return os.path.join(ASSET_BASE_PATH, relative_path)

def _str_to_tuple_key(s_key):
    """Converts a string key like "x,y" to an integer tuple (x,y)."""
    try:
        return tuple(map(int, s_key.split(',')))
    except ValueError:
        print(f"Warning: Could not convert portal key '{s_key}' to tuple.")
        return s_key

def _process_map_definitions(data):
    """Processes loaded map data, resolving paths and converting portal keys/positions."""
    processed_data = {}
    for map_key, map_info_original in data.items():
        map_info = map_info_original.copy()

        if "layout_file" in map_info:
            map_info["layout_file"] = _resolve_asset_path(map_info["layout_file"])
        if "background_image" in map_info:
            map_info["background_image"] = _resolve_asset_path(map_info["background_image"])
        if "dialogue_background_image" in map_info:
            map_info["dialogue_background_image"] = _resolve_asset_path(map_info["dialogue_background_image"])

        if "npcs" in map_info:
            processed_npcs = []
            for npc_config_original in map_info["npcs"]:
                npc_config = npc_config_original.copy()
                if "sprite_paths" in npc_config:
                    processed_sprite_paths = {}
                    for direction, sprite_info_original in npc_config["sprite_paths"].items():
                        sprite_info = sprite_info_original.copy()
                        if "path" in sprite_info:
                            sprite_info["path"] = _resolve_asset_path(sprite_info["path"])
                        processed_sprite_paths[direction] = sprite_info
                    npc_config["sprite_paths"] = processed_sprite_paths
                
                if "map_sprite_static_path" in npc_config and npc_config["map_sprite_static_path"]:
                    npc_config["map_sprite_static_path"] = _resolve_asset_path(npc_config["map_sprite_static_path"])
                processed_npcs.append(npc_config)
            map_info["npcs"] = processed_npcs

        if "portals" in map_info:
            processed_portals = {}
            for str_portal_loc, portal_data_original in map_info["portals"].items():
                portal_data = portal_data_original.copy()
                tuple_portal_loc = _str_to_tuple_key(str_portal_loc)
                if "target_player_pos" in portal_data and isinstance(portal_data["target_player_pos"], list):
                    portal_data["target_player_pos"] = tuple(portal_data["target_player_pos"])
                processed_portals[tuple_portal_loc] = portal_data
            map_info["portals"] = processed_portals
            
        processed_data[map_key] = map_info
    return processed_data

def load_map_definitions(filename="map_definitions.json"):
    """Loads map definitions from a JSON file."""
    filepath = os.path.join(DATA_BASE_PATH, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return _process_map_definitions(data)
    except FileNotFoundError:
        print(f"Error: Map definitions file not found at {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {filepath}: {e}")
        return {}

def load_story_definitions(filename="story_definitions.json"):
    """Loads story definitions from a JSON file."""
    filepath = os.path.join(DATA_BASE_PATH, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data # Stories typically don't have internal paths to resolve in this structure
    except FileNotFoundError:
        print(f"Error: Story definitions file not found at {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {filepath}: {e}")
        return {}

def get_default_npc_sprite_paths():
    """Returns the default sprite paths for NPCs, with resolved paths."""
    return {
        "frente": {"path": _resolve_asset_path("sprite_knight_frente.png"), "frames": 1}
    }
