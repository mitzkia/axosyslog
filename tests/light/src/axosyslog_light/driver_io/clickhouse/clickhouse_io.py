#!/usr/bin/env python
#############################################################################
# Copyright (c) 2025 Andras Mitzki <andras.mitzki@axoflow.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# As an additional exemption you are allowed to compile & link against the
# OpenSSL libraries as published by the OpenSSL project. See the file
# COPYING for details.
#
#############################################################################
from __future__ import annotations

from axosyslog_light.executors.process_executor import ProcessExecutor
# from psutil import Popen


class ClickhouseDockerExecutor():
    def __init__(self) -> None:
        self.__image_name = "clickhouse/clickhouse-server"
        self.__container_name = "clickhouse-container"

    def _start(self) -> None:
        command = ["docker", "run", "-d"]
        command += ["--network=host"]
        command += ["-v", "clickhouse_server_config.xml:/etc/clickhouse-server/config.xml"]
        command += ["--name", self.__container_name]
        command += ["--ulimit", "nofile=262144:262144"]
        command += [self.__image_name]

        stdout = "clickhouse_server_stdout.log"
        stderr = "clickhouse_server_stderr.log"

        return ProcessExecutor().start(command, stdout, stderr)

    def _stop(self) -> None:
        command = ["docker", "stop", self.__container_name]
        return ProcessExecutor().start(command, stdout=None, stderr=None)


class ClickhouseIO():
    def __init__(self) -> None:
        pass


# # docker run -d --network=host -v /home/micek/clickhouse-config2.xml:/etc/clickhouse-server/config.xml  --name some-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server
# # class LoggenDockerExecutor(LoggenExecutor):
# #     def __init__(self, image_name: str) -> None:
# #         self.__image_name = image_name
# #         super().__init__()
# #     def _start(self, start_params: LoggenStartParams, stderr: Path, stdout: Path, instance_index: int) -> Popen:
# #         paths: typing.Set[Path] = {
# #             Path.cwd().absolute(),
# #         }
# #         if start_params.read_file:
# #             paths.add(Path(start_params.read_file).parent.absolute())
# #         command = ["docker", "run", "--rm", "-i"]
# #         command += ["--entrypoint", "loggen"]
# #         command += ["--name", f"loggen_{instance_index}"]
# #         command += ["--workdir", str(Path.cwd().absolute())]
# #         command += ["--user", f"{os.getuid()}:{os.getgid()}"]
# #         command += ["-e", f"PUID={os.getuid()}", "-e", f"PGID={os.getgid()}"]
# #         command += ["--network", "host"]
# #         for path in paths:
# #             command += ["-v", f"{path}:{path}"]
# #         command += [self.__image_name]
# #         command += start_params.format()
# #         return ProcessExecutor().start(command, stdout, stderr)
# #     def _copy(self) -> LoggenExecutor:
# #         return LoggenDockerExecutor(self.__image_name)
# class ClickhouseDockerExecutor():
#     def __init__(self, image_name: str) -> None:
#         self.__image_name = image_name
#     def _start(self, instance_index: int) -> None:
#         command = [
#             "docker", "run", "--rm", "-i",
#             "--entrypoint", "loggen",
#             "--name", f"loggen_{instance_index}",
#             "--workdir", "/workdir",
#             "--user", f"{os.getuid()}:{os.getgid()}",
#             "--network", "host",
#             self.__image_name,
#         ]
#         # Execute the command to start the container
#         # This is a placeholder for actual execution logic
#         print(f"Starting Clickhouse Docker Executor with command: {' '.join(command)}")
# class ClickhouseIO():
#     def __init__(self) -> None:
#         pass
#     def start_db(self):
#         pass
#     def stop_db(self):
#         pass
#     # def write_message(self, message: str) -> None:
#     #     response = requests.post(self.__url, data=message)
#     #     if response.status_code != 200:
#     #         raise Exception(f"Failed to send message: {response.status_code} {response.text}")
#     # def write_json_message(self, message: dict) -> None:
#     #     response = requests.post(self.__url, json=message)
#     #     if response.status_code != 200:
#     #         raise Exception(f"Failed to send message: {response.status_code} {response.text}")
