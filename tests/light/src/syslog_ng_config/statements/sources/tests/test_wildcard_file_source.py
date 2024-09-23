
import pytest
from pathlib import Path
from src.syslog_ng_config.statements.sources.wildcard_file_source import WildcardFileSource

def test_generate_paths():
    base_dir = "/var/"
    filename_pattern = "almafa?.log"

    number_of_files = 5

    wildcard_file_source = WildcardFileSource(base_dir, filename_pattern)
    # expected_paths = [Path(base_dir) / f"{filename_pattern}{i}" for i in range(number_of_files)]
    
    # generated_paths = wildcard_file_source.generate_paths(number_of_files)
    
    # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    # print(generated_paths)
    
    # assert generated_paths == expected_paths
    
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1: %s" % wildcard_file_source.generate_paths(number_of_files))