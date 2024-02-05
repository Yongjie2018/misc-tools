#!/usr/bin/env python3

import os
import sys
import argparse
import tempfile
import tarfile
import zipfile
import re

from typing import List

tags_message = ["MESSAGE LOG"]


def _parse_syslog(lines: List[str]):
    """Split syslog lines into sel, dmesg and message
    """
    syslog = []
    res = {}
    tag = None
    res[tag] = []
    for line in lines:
        if line.startswith("TAG::"):
            tag = line.strip()[5:]
            res[tag] = []
        else:
            res[tag].append(line)
    for tag in tags_message:
        if tag in res:
            syslog.extend(res.get(tag, []))
    return syslog

def try_extract(archive_path: str, temp_dir: str, name_regex: str):
    tarfile_subfixes = ("tar.xz", "tar.gz", "tar", "tgz")
    zipfile_subfixes = ("zip", )
    archive_name = os.path.basename(archive_path)
    if any([archive_path.endswith(s) for s in tarfile_subfixes]):
        archive = tarfile.open(archive_path)
        names = archive.getnames()
    else:
        assert any([archive_path.endswith(s) for s in zipfile_subfixes])
        archive = zipfile.ZipFile(archive_path)
        names = archive.namelist()
    matched_names = [n for n in names if re.fullmatch(name_regex, n)]
    if len(matched_names) == 1:
        full_name = matched_names[0]
        archive.extract(full_name, temp_dir)
        dst_path = os.path.join(temp_dir, full_name)
        print(f"Extracted {full_name} in {archive_name}")
        return dst_path
    elif len(matched_names) == 0:
        print(f"Nothing matching {name_regex} in {archive_name}.")
        return None
    else:
        print(
            f"Multiple files matching {name_regex} in {archive_name}: {matched_names}")
        return None

def get_syslog_messages(archive_path: str):
    archive_name = os.path.basename(archive_path)
    syslog = None
    message = None
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Analyze OSsyslog
        print(tmp_dir)
        syslog_path = try_extract(archive_path, tmp_dir, r".*/sys__.*\.log")
        if syslog_path is None:
            print("No Syslog in {}.".format(archive_name))
        else:
            with open(syslog_path) as f:
                syslog = f.readlines()
    
    if syslog:
        message = _parse_syslog(syslog)
    return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", "-i")
    parser.add_argument("--outfile", "-o")
    args = parser.parse_args()
    if not args.infile or not args.outfile:
        print("Usage: sys.argv[0] --infile /path/to/input/shc-log.tar.xz --outfile /path/to/sys-log-messages.log")
        sys.exit(1)
    messages = get_syslog_messages(args.infile)
    if not messages:
        sys.exit(1)
    with open(args.outfile, "wt") as f:
        f.writelines(messages)
    sys.exit(0)
