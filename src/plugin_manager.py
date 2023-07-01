#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : plugin_manager.py

@Author     : hsn

@Date       : 4/15/23 2:32 PM

@Version    : 1.1.0
"""
import inspect
import shutil
import zipfile
from pathlib import Path
from typing import Union

from src.dynamic_obj_loader import DynamicObjLoader
from src.util.config_parser import ConfigParser


class PluginManager:
    """
    Plugin manager.
    """

    def __init__(self, config: ConfigParser = None, dol: DynamicObjLoader = None):
        """

        :param config: Global config
        :param dol: The dynamic object loader.
        """
        self.config: ConfigParser = config if config is not None else ConfigParser({})
        self.dcl: DynamicObjLoader = dol if dol is not None else DynamicObjLoader()

        self.plugin_folder: Path = Path(self.config.get_from_pointer('/plugin/folder', 'plugins'))

        self.plugins = {}

    def load_plugin(self, path: Union[Path, str]):
        """
        Load plugin from path.
        :param path: The path of plugin.
        :return:
        """
        plugin_path = self._get_plugin_path(path)

        if plugin_path.is_dir():
            # folder plugin
            # get plugin info

            with open(plugin_path / 'plugin.json', 'r') as f:

                plugin_info = ConfigParser(f)

            plugin_name: str = plugin_info.get_from_pointer('/name', None)
            plugin_main: str = plugin_info.get_from_pointer('/main', 'main.py')

            # copy config to temp folder
            plugin_work_folder = self.plugin_folder / plugin_name
            if not plugin_work_folder.exists():
                shutil.copytree(plugin_path, plugin_work_folder)

        elif plugin_path.suffix in ['.pyz', '.zip']:
            with zipfile.ZipFile(plugin_path, 'r') as z, z.open('plugin.json', 'r') as f:
                plugin_info = ConfigParser(f)
                plugin_name = plugin_info.get_from_pointer('/name', None)
                plugin_main: str = plugin_info.get_from_pointer('/main', 'main.py')

                plugin_work_folder = self.plugin_folder / plugin_name
                z.extractall(plugin_work_folder)

        else:
            raise NotImplementedError(f'Plugin type {plugin_path.suffix} not implemented.')

        self.plugins[plugin_name] = plugin_info
        plugin_main_path = (plugin_work_folder / "/".join(plugin_main.split('.'))).parent.with_suffix('.py')

        def _try_to_load(path_, obj_name_):
            try:
                return self.dcl.load_obj(path=path_, obj_name=obj_name_)
            except AttributeError:
                return None

        for i in [plugin_main, 'main', 'Main', '__main__', '__Main__']:
            if not (main_func := _try_to_load(plugin_main_path, i)):
                break
        else:
            raise ImportError(f'No main function found in {plugin_main}')

        args = {"dcl": self.dcl, "config": self.config, "work_folder": plugin_work_folder}
        params = [i for i in inspect.signature(main_func).parameters]

        main_func(**{i: args[i] for i in params if i in args})
        return plugin_info, plugin_work_folder

    def _get_plugin_path(self, path):
        if isinstance(path, str):

            if Path(path).exists():
                plugin_path = Path(path)
            elif (self.plugin_folder / path).exists():
                plugin_path = self.plugin_folder / path
            elif (self.plugin_folder / path).with_suffix('.pyz').exists():
                plugin_path = (self.plugin_folder / path).with_suffix('.pyz')
            elif (self.plugin_folder / path).with_suffix('.zip').exists():
                plugin_path = (self.plugin_folder / path).with_suffix('.zip')
            else:
                raise FileNotFoundError(f'Plugin {path} not found.')

        elif isinstance(path, Path):
            plugin_path = path
        else:
            raise TypeError(f'path must be str or Path, not {type(path)}')

        if not Path(path).exists():
            raise FileNotFoundError(f'Plugin {path} not found.')
        return plugin_path

    def load_plugins(self):
        if not self.plugin_folder.exists():
            self.plugin_folder.mkdir()
        for i in self.plugin_folder.iterdir():
            if i.is_dir() or i.suffix == '.pyz' or i.suffix == '.zip':
                yield self.load_plugin(i)
