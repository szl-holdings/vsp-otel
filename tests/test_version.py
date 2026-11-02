"""The installed distribution and public runtime must report the same version."""

from importlib.metadata import version

import vsp_otel


def test_runtime_version_matches_installed_distribution():
    assert vsp_otel.__version__ == version("vsp-otel")
