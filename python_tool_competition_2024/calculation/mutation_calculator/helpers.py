#
# Copyright (c) 2023 Nicolas Erni.
#
# This file is part of python-tool-competition-2024
# (see https://github.com/ThunderKey/python-tool-competition-2024/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""Basic helpers for mutation calculators."""

import re


def find_matching_line(
    pattern: re.Pattern[str], lines: tuple[str, ...]
) -> re.Match[str]:
    """Find the first line the fully matches the regex."""
    for line in lines:
        match = pattern.fullmatch(line)
        if match is not None:
            return match
    msg = f"No match for {pattern.pattern!r} found in {lines}"
    raise RuntimeError(msg)
