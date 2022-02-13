import json
import os


class JsonData:
    @staticmethod
    def read_from_json():
        """
        Method for reading from settings.json JSON file.
        :return:
        """
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'chessdsl', 'settings.json')
        json_file = open(settings_path, "r", encoding="utf8")
        data = json.loads(json_file.read())
        json_file.close()

        return data

    @staticmethod
    def get_json_data(json_data):
        """
        Method for getting most used values needed for making GUI view.
        :return:
        """
        name = json_data['NAME']
        board_width = json_data['BOARD_WIDTH']
        board_height = json_data['BOARD_HEIGHT']
        settings = json_data['SETTINGS']

        return name, board_width, board_height, settings

    @staticmethod
    def write_to_json(json_data):
        """
        Method for writing into settings.json JSON file.
        :param json_data:
        :return:
        """
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'chessdsl', 'settings.json')
        json_file = open(settings_path, "w", encoding="utf8")
        json.dump(json_data, json_file, indent=2, ensure_ascii=False)
        json_file.close()
