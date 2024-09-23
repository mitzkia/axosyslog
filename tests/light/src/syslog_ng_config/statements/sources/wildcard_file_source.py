import logging
from pathlib import Path

from src.driver_io.file.file_io import FileIO
from src.syslog_ng_config.statements.sources.source_driver import SourceDriver
from src.syslog_ng_ctl.driver_stats_handler import DriverStatsHandler

logger = logging.getLogger(__name__)


class WildcardFileSource(SourceDriver):
    def __init__(self, base_dir, filename_pattern, **options):
        self.driver_name = "wildcard-file"
        self.set_base_dir(base_dir)
        self.set_filename_pattern(filename_pattern)
        self.set_full_wildcard_path()
        self.full_dir_path = Path("/".join(str(self.get_full_wildcard_path()).split("/")[:-1]))
        self.full_dir_path.mkdir(parents=True, exist_ok=True)

        self.paths_and_io_map = []

        options["base_dir"] = self.get_base_dir()
        options["filename_pattern"] = self.get_filename_pattern()
        super(WildcardFileSource, self).__init__(options=options)
        self.stats_handler = DriverStatsHandler(group_type=self.group_type, driver_name="file")

    def get_base_dir(self):
        return self.base_dir

    def set_base_dir(self, base_dir):
        self.base_dir = Path(base_dir)

    def get_filename_pattern(self):
        return self.filename_pattern

    def set_filename_pattern(self, filename_pattern):
        self.filename_pattern = Path(filename_pattern)

    def get_full_wildcard_path(self):
        return self.full_wildcard_path

    def set_full_wildcard_path(self):
        self.full_wildcard_path = Path(self.base_dir) / Path(self.filename_pattern)

    def generate_paths(self, number_of_files):
        return [
            str(self.get_full_wildcard_path()).replace("*", "_MATCHING_FOR_WILDCARD_%s" % i).replace("?", "_W_%s" % i)
            for i in range(number_of_files)
        ]

    def generate_file_ios(self, paths):
        return [FileIO(path) for path in paths]

    def generate_paths_for_wildcard_pattern(self, number_of_files=1):
        for file_counter in range(number_of_files):
            self.paths_and_io_map.append(
                {
                    "path": self.generate_paths(number_of_files)[file_counter],
                    "io": self.generate_file_ios(self.generate_paths(number_of_files))[file_counter],
                }
            )

    def get_paths_and_io_map(self):
        return self.paths_and_io_map


    def write_log(self, formatted_log, counter=1):
        for path_and_io in self.get_paths_and_io_map():
            for _ in range(counter):
                path_and_io["io"].write(formatted_log)
                logger.info(
                    "Content has been written to\nresource: {}\n"
                    "number of times: {}\n"
                    "content: {}\n".format(path_and_io["path"], counter, formatted_log),
                )

    def close_file(self):
        self.io.close_writeable_file()
