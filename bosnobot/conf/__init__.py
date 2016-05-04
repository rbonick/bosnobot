"""
Settings and configuration for bosnobot. This is based heavily on django.conf.
"""
import os

from bosnobot.conf import global_settings


class Settings(object):
    def __init__(self):
        for setting in dir(global_settings):
            if setting == setting.upper():
                setattr(self, setting, getattr(global_settings, setting))

settings = Settings()
