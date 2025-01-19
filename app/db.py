
# app/db.py
# This file handles database interactions (currently file-based, later SQLite).
import json

def save_parsed_data(data, filename="parsed_data.json"):
    """
    Saves the parsed data to a JSON file.

    Args:
        data: The data to save.
        filename: The name of the file to save to.
    """
    # TODO: Implement data saving logic (currently to JSON)
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_parsed_data(filename="parsed_data.json"):
    """
    Loads parsed data from a JSON file.

    Args:
        filename: The name of the file to load from.

    Returns:
        The loaded data.
    """
    # TODO: Implement data loading logic (currently from JSON)
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
