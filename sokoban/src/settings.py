import json
import os

from os.path import (join,
                     expanduser, dirname)


class Settings:
    USER_HOME = None
    HOME_DIR = '.sokoban/'
    SAVES_DIR = 'saves/'
    LEVELS_DIR = 'levels/'
    CONFIG = 'config.json'
    MAPS = '../maps/'

    def __init__(self):
        self.canvas_width = 800
        self.canvas_height = 800
        self.square_width = 20
        self.square_height = 20

    def load(self):
        with open(Settings.get_path(Settings.CONFIG), 'r') as cfg_file:
            to_update = {}
            external_cfg = json.load(cfg_file)
            for name, value in self.get_settings():
                to_update[name] = external_cfg.get(name, value)
            self.__dict__.update(to_update)

    def list_levels(self):
        for root, dirs, files in os.walk(Settings.get_path(Settings.LEVELS_DIR)):
            for level_file in files:
                yield join(root, level_file)

    def list_saves(self):
        for root, dirs, files in os.walk(self.get_path(Settings.SAVES_DIR)):
            for f in files:
                yield f, join(root, f)

    def get_settings(self):
        _valid_types = {str, int, float, type(None)}
        for name, value in self.__dict__.items():
            if (not name.startswith('_')
                    and type(value) in _valid_types):
                yield name, value

    @staticmethod
    def get_home():
        if Settings.USER_HOME is None:
            Settings.USER_HOME = expanduser("~")
        return join(Settings.USER_HOME, Settings.HOME_DIR)

    @staticmethod
    def get_path(path, *paths):
        return join(Settings.get_home(), path, *paths)

    def save(self):
        with open(Settings.get_path(Settings.CONFIG), 'w') as cfg_file:
            json.dump(dict(self.get_settings()), cfg_file, indent=2)

    def create_file_structure(self):
        if not os.path.exists(Settings.get_home()):
            os.makedirs(Settings.get_path(Settings.LEVELS_DIR))
            os.makedirs(Settings.get_path(Settings.SAVES_DIR))
            self.save()


class LevelHandler:

    def __init__(self, settings):
        self.settings = settings

    def load_level(self, level):
        level_path = None
        for lvl_name, level_path in self.list_levels():
            if level == lvl_name:
                break
        return self.load_file(level_path)

    @staticmethod
    def load_file(path):
        with open(path, 'r') as level_file:
            return [line.strip() for line in level_file]

    def save(self, storage, save_name):
        save_path = self.settings.get_path(Settings.SAVES_DIR, save_name)
        LevelHandler.write_file(save_path, storage.marshall())

    def load(self, save_name):
        save_path = self.settings.get_path(Settings.SAVES_DIR, save_name)
        return self.load_file(save_path)

    @staticmethod
    def write_file(path, plan):
        with open(path, 'wt', ) as f:
            f.write('\n'.join(plan))
            f.write('\n')

    def list_levels(self):
        for root, dirs, files in os.walk(join(dirname(__file__),
                                              Settings.MAPS)):
            for f in files:
                yield f, join(root, f)

    def list_saves(self):
        for root, dirs, files in os.walk(
                self.settings.get_path(Settings.SAVES_DIR)):
            for f in files:
                yield f, join(root, f)
