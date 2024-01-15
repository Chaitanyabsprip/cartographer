import os
from pathlib import Path

import yaml


def get_config_dir() -> str:
    """Locate a platform-appropriate config directory for cartographer to use

    Does not ensure that the config directory exists.
    """
    # Linux, Unix, AIX, etc.
    if os.name == "posix":  # and sys.platform != "darwin":
        xdg = os.environ.get("XDG_CONFIG_HOME", None) or os.path.expanduser(
            "~/.config"
        )
        return os.path.join(xdg, "cartographer")

    # # Mac OS
    # elif sys.platform == "darwin":
    #     return Path(os.path.expanduser("~"), "Library/configs/flit")
    #
    # Windows (hopefully)
    else:
        local = os.environ.get("LOCALAPPDATA", None) or os.path.expanduser(
            "~\\AppData\\Local"
        )
        return os.path.join(local, "flit")


def get_cache_dir() -> str:
    """Locate a platform-appropriate cache directory for cartographer to use

    Does not ensure that the cache directory exists.
    """
    # Linux, Unix, AIX, etc.
    if os.name == "posix":  # and sys.platform != "darwin":
        xdg = os.environ.get("XDG_CACHE_HOME", None) or os.path.expanduser(
            "~/.cache"
        )
        return os.path.join(xdg, "cartographer")

    # # Mac OS
    # elif sys.platform == "darwin":
    #     return Path(os.path.expanduser("~"), "Library/Caches/flit")
    #
    # Windows (hopefully)
    else:
        local = os.environ.get("LOCALAPPDATA", None) or os.path.expanduser(
            "~\\AppData\\Local"
        )
        return Path(local, "flit")


def create_app_dirs():
    cache_dir = get_cache_dir()
    config_dir = get_config_dir()
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)


class Config:
    def __init__(self):
        create_app_dirs()
        config_filepath = os.path.join(get_config_dir(), "config.yml")
        config = {}
        if os.path.exists(config_filepath):
            with open(config_filepath, "r") as file:
                config = yaml.safe_load(file)

        self.embedding_file = config.get(
            "embeddings_file", os.path.join(get_cache_dir(), ".embeddings_bin")
        )
        self.transformer_name = config.get(
            "transformer_name", "msmarco-distilbert-base-v4"
        )
        self.paths = config.get("paths", [])
        self.paths = map(lambda x: os.path.expanduser(x), self.paths)
        self.ignore_paths = config.get("ignore_paths", [])
        self.extensions = config.get("extensions", [])
        self.blacklist_extensions = config.get(
            "blacklist_extensions", not self.extensions
        )
