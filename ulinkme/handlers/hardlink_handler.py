import os
from typing import Union
from watchdog.events import (
    FileSystemEventHandler,
    DirCreatedEvent,
    FileCreatedEvent,
    DirDeletedEvent,
    FileDeletedEvent,
    DirMovedEvent,
    FileMovedEvent,
)
import logging
import os.path as path
from os.path import relpath, exists, abspath, dirname

logger = logging.getLogger(__name__)

EVENT_HANDLER_CREATE = 0x1
EVENT_HANDLER_DELETE = 0x2
EVENT_HANDLER_MOVE = 0x4


def _get_relative_path(base: str, abspath: str) -> str:
    return relpath(abspath, base)


def _get_abs_path(base: str, relpath: str) -> str:
    return abspath(path.join(base, relpath))


def _recursive_create_dir(dirname: str):
    os.makedirs(dirname, exist_ok=True)


class HardLinkEventHandler(FileSystemEventHandler):
    def __init__(self, name_base, target_base, events=EVENT_HANDLER_CREATE) -> None:
        super().__init__()
        self.name_base = name_base
        self.target_base = target_base
        self.events = events

    def _prepare_parent_dir(self, target_abs: str) -> str:

        target_relative = _get_relative_path(self.target_base, target_abs)
        name_abs = _get_abs_path(self.name_base, target_relative)
        _recursive_create_dir(dirname(name_abs))
        return name_abs

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        if self.events & EVENT_HANDLER_CREATE:
            target_abs = abspath(event.src_path)
            logger.info(f"{target_abs} created")
            name_abs = self._prepare_parent_dir(target_abs)
            if not exists(name_abs):
                if isinstance(event, DirCreatedEvent):
                    os.makedirs(name_abs, exist_ok=True)
                    logger.info(f"create folder {name_abs} -> {target_abs}")
                else:
                    os.link(dst=name_abs, src=target_abs)
                    logger.info(f"create hardlink {name_abs} -> {target_abs}")
            else:
                logger.warning(f"folder/file {name_abs} exists")
        return super().on_created(event)

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]):
        if self.events & EVENT_HANDLER_DELETE:
            logger.info(f"{event.src_path} deleted")
            target_rel = _get_relative_path(self.target_base, event.src_path)
            name_abs = _get_abs_path(self.name_base, target_rel)
            if exists(name_abs):
                if isinstance(event, DirDeletedEvent):
                    logger.info(f"remove directory {name_abs} -> {event.src_path}")
                    os.rmdir(name_abs)
                else:
                    logger.info(f"unlink file {name_abs} -> {event.src_path}")
                    os.unlink(name_abs)

        return super().on_deleted(event)

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]):
        if self.events & EVENT_HANDLER_MOVE:
            logger.info(f"{event.src_path} moved to {event.dest_path}")
            if event.src_path.startswith(
                self.target_base
            ) and event.dest_path.startswith(self.target_base):
                # currently only interact with in-target move event
                old_target_rel = _get_relative_path(self.target_base, event.src_path)
                new_target_rel = _get_relative_path(self.target_base, event.dest_path)
                old_name_abs = _get_abs_path(self.name_base, old_target_rel)
                new_name_abs = _get_abs_path(self.name_base, new_target_rel)
                if exists(old_name_abs):
                    new_target_abs = abspath(event.dest_path)
                    self._prepare_parent_dir(new_target_abs)
                    os.rename(old_name_abs, new_name_abs)
                    logger.info(
                        f"move file from {old_name_abs} -> {event.src_path} to {new_name_abs} -> {event.dest_path}"
                    )
                else:
                    logger.warning(f"{old_name_abs} file/folder doesn't not exists")
        return super().on_moved(event)
