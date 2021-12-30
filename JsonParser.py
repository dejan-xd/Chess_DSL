"""
    Create Library for JSON parser.
"""
import json


class JsonParser:
    def __init__(self):
        self.file = "settings.json"
        self.read = "r"
        self.write = "w"
        self.utf = "utf8"
        self.read_json()

    def read_json(self):
        json_file = open(self.file, self.read, encoding=self.utf)
        self.data = json.loads(json_file.read())
        json_file.close()

    def get_by_key(self, key1, key2=None):
        if key2 is None:
            return self.data[key1]
        else:
            return self.data[key1][key2]

    def set_new_json(self, new_json):
        json_file = open(self.file, self.write, encoding=self.utf)
        json.dump(new_json, json_file, indent=2, ensure_ascii=False)
        json_file.close()

    def get_json_data(self):
        name = self.data['NAME']
        board_width = self.data['BOARD_WIDTH']
        board_height = self.data['BOARD_HEIGHT']
        settings = self.data['SETTINGS']

        return name, board_width, board_height, settings

    def __del__(self):
        self.data = None
