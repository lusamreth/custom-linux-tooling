import os
import multiprocessing
import subprocess
import logging
from typing import Optional
import yaml
import shutil


logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)


def setupLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


def is_binary(filename):
    with open(filename, "rb") as f:
        try:
            f.read(1024).decode("utf-8")
        except UnicodeDecodeError:
            return True
    return False


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


HOME_PREFIX = "/home/lusamreth"
DOWNLOAD_PATH = "/Downloads"
"""
    - sample format : 
    ext :
        - pdf
        - jpeg
        - png
    directory : "Pictures"

    TODO LIST :
    - create a reversible state using checksum (for backups)
    - create a skip scanner of folder / files
    - add "move / delete" function
"""


def readConfig():
    with open(f"sample_cfg.yaml", "r") as f:
        output = yaml.safe_load(f)
        conf = Config(**output)
        conf.parseBlocks()
        print(output)
        return conf


class ConfigBlock:
    def __init__(self, name, ext, directory, skip):
        self.name = name
        if len(ext) == 0:
            raise Exception("Cannot accept empty extensions")
        self.ext = ext
        self.directory = directory
        self.root = ""
        self.skip = skip

    def insert_root(self, root):
        self.root = root
        self.directory = self.root + "/" + self.directory

    def info(self):
        print("\n")
        print(
            "Name : {}\nExt : {}\nDirectory : {}\n".format(
                self.name, ",".join(self.ext), self.directory
            )
        )


supported_operations = {"CREATE", "MOVE"}
supported_states = {"FILE", "DIR"}


class DIRStrategy:
    def __init__(self, logger=logging):
        self.logger = logger
        pass

    def create(self, url):
        existed = False
        try:
            _ = os.listdir(url)
        except FileNotFoundError:
            print("Directory is not yet created", url)
            existed = True
        if existed:
            # raise Exception("Fold is already exists")
            self.logger.warn("Fold is already exists")
        print("GIV", url)
        self.logger.log(
            1,
            "GIVEN URL",
        )
        return os.mkdir(url)


class StateOperation:
    CREATED = "CREATE"
    REMOVED = "REMOVED"
    MOVE = "MOVE"


class FileState:
    def __init__(
        self, state_type: str, operation: StateOperation | str
    ):
        if state_type not in supported_states:
            raise ValueError("")
        if operation not in supported_operations:
            raise ValueError("")
        self.state_type = state_type
        self.operation = operation
        self.isResolved = False

    def resolveState(self, params):
        if self.state_type == "DIR" and not self.isResolved:
            try:
                DIRStrategy().create(params["url"])
            except Exception as e:
                return
            self.isResolved = True

    # def


class Config:
    def __init__(self, folder, blocks, mode):
        self.folder = folder
        self.blocks = blocks
        self.mode = mode

        self.ext_set = {}
        self.block_table = {}
        self.sync_state = {}

    def parseBlocks(self):
        try:
            for block in self.blocks:
                print(block)

                block = ConfigBlock(**block)
                block.insert_root(self.folder)
                block.info()

                self.block_table[block.name] = block
                self.ext_set = dict.fromkeys(block.ext, block.name)

                try:
                    _dir = os.listdir(block.directory)
                except FileNotFoundError:
                    self.sync_state[block.name] = FileState(
                        "DIR", StateOperation.CREATED
                    )
                    logging.warn("Directory is not yet created")

        except Exception as e:
            print("Getting exception during parsing")
            print(e)

    def sync_block(self, block: ConfigBlock):
        name = block.name
        if self.sync_state.get(name):
            self.sync_state[name].resolveState(
                {"url": block.directory}
            )

    def ext_in_block(self, input_ext) -> Optional[ConfigBlock]:
        if self.ext_set.get(input_ext):
            name = self.ext_set[input_ext]
            block = self.block_table[name]
            return block
        else:
            return None


def crawler(config: Config, debug=False):
    # resolved = False
    # config.sync_state[ext].resolveState()
    logger = setupLogger("crawler-logger")
    try:
        download_path = HOME_PREFIX + DOWNLOAD_PATH
        for entry in scantree(download_path):
            if entry.is_file():
                splited = os.path.splitext(entry.name)
                ext = splited[1][1:]
                block = config.ext_in_block(ext)
                if block is not None:
                    config.sync_block(block)
                    # print(config.mode == "copy")

                    if config.mode == "copy":
                        logger.info("COPYING {}".format(entry.path))
                        shutil.copy(
                            entry.path,
                            block.directory,
                        )

        # for file in download_files:
    except FileNotFoundError as e:
        print(e)

    pass


def main():
    config = readConfig()
    crawler(config)
    pass


if __name__ == "__main__":
    main()
