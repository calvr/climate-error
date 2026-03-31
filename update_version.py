#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import re
from datetime import date
from pathlib import Path


def update_version():
    #ROOT = Path(__file__).resolve().parents[1]
    ROOT = Path(__file__).resolve().parents[0]
    pyproject = ROOT / "pyproject.toml"
    citation = ROOT / "CITATION.cff"
    # extract version from pyproject.toml
    text = pyproject.read_text()
    version_match = re.search(r'version\s*=\s*"([^"]+)"', text)
    assert version_match, "Version not found in pyproject.toml"
    version = version_match.group(1)
    print(f"[metadata] Using version: {version}")
    # update CITATION.cff version
    cff = citation.read_text()
    cff = re.sub(
        r'version:\s*"[0-9a-zA-Z\.\-]+"',
        f'version: "{version}"',
        cff,
    )
    # update date-released
    today = date.today().isoformat()
    cff = re.sub(
        r'date-released:\s*"[0-9\-]+"',
        f'date-released: "{today}"',
        cff,
    )
    citation.write_text(cff, encoding="utf-8")
    print("[metadata] CITATION.cff updated.")


if __name__ == '__main__':
    update_version()

