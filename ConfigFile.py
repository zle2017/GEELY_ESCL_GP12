#coding=utf-8

from configobj import ConfigObj
import os
import glob
from _ast import Str


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class Config:

    file_dir = Str()

    def get_list(self):
        _file_list_name = []
        if os.path.isdir(self.file_dir):
            for filename in os.listdir(self.file_dir):
                _file_list_name.append(filename.rstrip('.ini'))
        return _file_list_name

    def get_value(self, filename):
        value_dict = ConfigObj(self.file_dir + filename + '.ini')
        return value_dict


if __name__ == "__main__":
    pass
