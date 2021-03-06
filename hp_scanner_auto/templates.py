"""
Manage templating options for user
"""

import json
import os

_BASE = os.path.dirname(__file__)
_FOLDERS_TEMPLATES = os.path.join(_BASE, 'hp-scanner-folders.json')
_FILES_TEMPLATES = os.path.join(_BASE, 'hp-scanner-files.json')


class TemplateManager:
    """Manage Folder and File Template Options"""
    def __init__(self, filepath):
        self.config_file = filepath
        try:
            with open(self.config_file) as fp:
                self._values = json.load(fp)
        except FileNotFoundError:
            self._values = []

    def append(self, val):
        self._values.append(val)

        with open(self.config_file, 'w+') as fp:
            json.dump(sorted(self._values), fp, indent=4)

    def __iter__(self):
        return iter(self._values)

    def __bool__(self):
        return bool(self._values)


folders = TemplateManager(_FOLDERS_TEMPLATES)
files = TemplateManager(_FILES_TEMPLATES)
