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
Template generation dialog
"""

__all__ = ['Templater']

from PyQt4 import QtCore, QtGui

from .base import ServiceDialog

# all methods might need 'self' in the future, pylint:disable=R0201


class Templater(ServiceDialog):
    """
    Provides a dialog for building an on-the-fly TTS tag in Anki's card
    layout editor.
    """

    __slots__ = [
        '_card_layout',  # reference to the card layout window
    ]

    def __init__(self, card_layout, *args, **kwargs):
        """
        Sets our title.
        """

        self._card_layout = card_layout
        super(Templater, self).__init__(
            title="Add On-the-Fly TTS Tag",
            *args, **kwargs
        )

    # UI Construction ########################################################

    def _ui_control(self):
        """
        Returns the superclass's text and preview buttons, adding our
        field input selector, then the base class's cancel/OK buttons.
        """

        header = QtGui.QLabel("Tag Options")
        header.setFont(self._FONT_HEADER)

        intro = QtGui.QLabel(
            "In review mode, AwesomeTTS can automatically read the text from "
            "any <tts> tags in the template, generating on-the-fly audio "
            "playback. You can specify a specific note field to read from or "
            "customize the text yourself."
        )
        intro.setFont(self._FONT_INFO)
        intro.setTextFormat(QtCore.Qt.PlainText)
        intro.setWordWrap(True)

        hint = QtGui.QLabel(
            "Normally, the content of <tts> tags are visible like any other "
            "HTML tag, but you can alter their appearance with inline CSS or "
            "the note-wide style rules."
        )
        hint.setFont(self._FONT_INFO)
        hint.setTextFormat(QtCore.Qt.PlainText)
        hint.setWordWrap(True)

        layout = super(Templater, self)._ui_control()
        layout.addWidget(header)
        layout.addWidget(intro)
        layout.addWidget(hint)
        layout.addLayout(self._ui_control_fields())
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_control_fields(self):
        """
        Returns a dropdown box to let the user select a source field.
        """

        layout = QtGui.QGridLayout()

        for row, label, name, options in [
            (0, "Field:", 'field', [
                ('', "customize the tag's content"),
            ] + [
                (field, field)
                for field in sorted({
                    field['name']
                    for field in self._card_layout.model['flds']
                })
            ]),

            (1, "Visibility:", 'hide', [
                ('normal', "insert the tag as-is"),
                ('inline', "hide just this tag w/ inline CSS"),
                ('global', "add rule to hide any TTS tag for this note type"),
            ]),

            (2, "Add to:", 'target', [
                ('front', "Front Template"),
                ('back', "Back Template"),
            ]),
        ]:
            label = QtGui.QLabel(label)
            label.setFont(self._FONT_LABEL)

            layout.addWidget(
                label,
                row, 0,
            )
            layout.addWidget(
                self._ui_control_fields_dropdown(name, options),
                row, 1,
            )

        return layout

    def _ui_control_fields_dropdown(self, name, options):
        """
        Returns a dropdown with the given list of options.
        """

        dropdown = QtGui.QComboBox()
        dropdown.setObjectName(name)
        for value, label in options:
            dropdown.addItem(label, value)

        return dropdown

    def _ui_buttons(self):
        """
        Adjust title of the OK button.
        """

        buttons = super(Templater, self)._ui_buttons()
        buttons.findChild(QtGui.QAbstractButton, 'okay').setText("&Insert")

        return buttons
