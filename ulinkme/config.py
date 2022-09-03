from dataclasses import dataclass
import json
import os
from os.path import exists, abspath, isdir
import time
from typing import Union
import logging
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from .handlers.hardlink_handler import (
    HardLinkEventHandler,
    EVENT_HANDLER_CREATE,
    EVENT_HANDLER_DELETE,
    EVENT_HANDLER_MOVE,
)

logger = logging.getLogger(__name__)


class Link:
    def __init__(self, target: str, name: str, recursive: bool, events: list) -> None:
        if not exists(target):
            raise FileNotFoundError(f"Link target {target} not found")
        if not isdir(target):
            raise NotImplementedError(
                f"Target {target} is required to be a folder by now"
            )
        if not isdir(name):
            raise NotImplementedError(f"Name {name} is required to be a folder by now")
        if not exists(name):
            logger.info(f"{name} doesn't exists, create one")
            os.makedirs(name, exist_ok=True)
        self.target = abspath(target)
        self.name = abspath(name)
        self.recursive = recursive
        events_flag = 0x0
        for event in events:
            if event == "create":
                events_flag |= EVENT_HANDLER_CREATE
            elif event == "delete":
                events_flag |= EVENT_HANDLER_DELETE
            elif event == "move":
                events_flag |= EVENT_HANDLER_MOVE
        self.events = events_flag
        self.watch = None
        self.linker = None

    def schedule(self, observer: Observer):
        logger.info(
            f"scheduled a link from {self.name} -> {self.target}, event mask: 0x{self.events:02x}"
        )
        self.linker = HardLinkEventHandler(self.name, self.target, self.events)
        self.watch = observer.schedule(self.linker, self.target, self.recursive)


class Config:
    def __init__(
        self, loglevel: Union[int, str], logdir: str, links: list[Link]
    ) -> None:
        log_str_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }
        if isinstance(loglevel, str):
            if loglevel in log_str_mapping:
                loglevel = log_str_mapping[loglevel.lower()]
        self.loglevel = loglevel
        self.logdir = logdir
        self.links = links

    def init_logging(self):
        if self.logdir:
            logging.basicConfig(
                level=self.loglevel,
                format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                datefmt="%m-%d %H:%M",
                filename=os.path.join(self.logdir, "ulinkme.log"),
                filemode="w",
            )
        else:
            logging.basicConfig(
                level=self.loglevel,
                format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                datefmt="%m-%d %H:%M",
            )

    def init_observer(self):
        self.observer = Observer()
        for link in self.links:
            link.schedule(self.observer)

    def loop(self, timeout=1):
        self.observer.start()
        try:
            while True:
                time.sleep(timeout)
        finally:
            self.observer.stop()
            self.observer.join()


DEFAULT_CONFIG_JSON = {"log": {"level": "warning", "logdir": None}, "links": []}


def generate_default_config() -> Config:
    print("config argument not found, fallback to default config")
    return _dispatch_config_from_json(DEFAULT_CONFIG_JSON)


def dispatch_config_from_file(filename: str) -> Config:
    if not os.path.exists(filename):
        raise FileNotFoundError(f"file {filename} not found")
    _, extension = os.path.splitext(filename)
    with open(filename, "r") as foo:
        if extension == ".json":
            data = json.load(foo)
            return _dispatch_config_from_json(data)
        else:
            raise NotImplementedError(
                f"config file extension {extension} not supported"
            )


def _dispatch_config_from_json(data) -> Config:
    loglevel = data.get("log", DEFAULT_CONFIG_JSON["log"]).get("level")
    logdir = data.get("log", DEFAULT_CONFIG_JSON["log"]).get("logdir")
    links_list = data.get("links", [])
    links = []
    for link in links_list:
        links.append(
            Link(
                target=link.get("target"),
                name=link.get("name"),
                recursive=link.get("recursive", True),
                events=link.get("events", []),
            )
        )
    return Config(loglevel, logdir, links)
