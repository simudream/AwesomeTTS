# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
#
# Copyright (C) 2014       Anki AwesomeTTS Development Team
# Copyright (C) 2014       Dave Shifflett
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Service implementation for Festival Speech Synthesis System
"""

__all__ = ['Festival']

from .base import Service
from .common import Trait


class Festival(Service):
    """
    Provides a Service-compliant implementation for Festival.
    """

    __slots__ = [
        '_version',       # we get this while testing for the festival binary
        '_voice_list',    # list of installed voices as a list of tuples
    ]

    NAME = "Festival"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Verifies existence of the `festival` and `text2wave` binaries
        and scans `/usr/share/festival/voices` for available voices.

        TODO: Is it possible to get Festival on Windows or Mac OS X? If
        so, what paths or binary location differences might there be?
        """

        if not self.IS_LINUX:
            raise EnvironmentError(
                "AwesomeTTS only knows how to work with the Linux version of "
                "Festival at this time."
            )

        super(Festival, self).__init__(*args, **kwargs)

        self._version = self.cli_output('festival', '--version').pop(0)
        self.cli_call('text2wave', '--help')

        import os
        base_dir = '/usr/share/festival/voices'
        self._voice_list = [
            (voice_dir, "%s (%s)" % (voice_dir, lang_dir))
            for lang_dir in sorted(os.listdir(base_dir))
            if os.path.isdir(os.path.join(base_dir, lang_dir))
            for voice_dir in sorted(os.listdir(os.path.join(base_dir,
                                                            lang_dir)))
            if os.path.isdir(os.path.join(base_dir, lang_dir, voice_dir))
        ]

        if not self._voice_list:
            raise EnvironmentError("No usable voices found in %s" % base_dir)

    def desc(self):
        """
        Returns a version string with terse description and release
        date, obtained when verifying the existence of the `festival`
        binary.
        """

        return "%s (%d voices)" % (self._version, len(self._voice_list))

    def options(self):
        """
        Provides access to voice and volume.
        """

        voice_lookup = {
            self.normalize(voice[0]): voice[0]
            for voice in self._voice_list
        }

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)

            return (
                voice_lookup[normalized] if normalized in voice_lookup
                else value
            )

        return [
            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=transform_voice,
            ),

            dict(
                key='volume',
                label="Volume",
                values=(10, 250, "%"),
                transform=int,
                default=100,
            ),
        ]

    def run(self, text, options, path):
        """
        Write a temporary input text file, calls `text2wave` to write a
        temporary wave file, and then transcodes that to MP3.
        """

        input_file = self.path_input(text)
        output_wav = self.path_temp('wav')

        try:
            self.cli_call(
                'text2wave',
                '-o', output_wav,
                '-eval', '(voice_%s)' % options['voice'],
                '-scale', options['volume'] / 100.0,
                input_file,
            )

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
            )

        finally:
            self.path_unlink(input_file, output_wav)
