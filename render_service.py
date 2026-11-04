import os

import verovio

from music21 import clef, stream
from music21.musicxml.m21ToXml import GeneralObjectExporter
from music_stream import composition_to_stream

# Verovio's fonts live in the package's data folder. It only finds them on its own
# in the main thread; Flask serves pages from worker threads, so set the path
# explicitly (otherwise: "font resources are not available").
VEROVIO_RESOURCES = os.path.join(os.path.dirname(verovio.__file__), "data")

# How the music is laid out in the editor (NTT-54):
# no "Music21 Fragment" title or footer, page height fitted to the music,
# the music font embedded in the SVG so browsers draw every symbol,
# and a page width/scale that fits the editor's staff area.
DISPLAY_OPTIONS = {
    "header": "none",
    "footer": "none",
    "adjustPageHeight": True,
    "smuflTextFont": "embedded",
    "pageWidth": 2100,
    "scale": 45,
}


def composition_to_svg(composition):
    """Convert a database composition into sheet music SVG."""

    # Step 1: Convert database notes to a music21 Stream
    melody = composition_to_stream(composition)

    # An empty composition uses a placeholder in the UI
    if not list(melody.notesAndRests):
        return ""

    # Step 2: Add a treble clef
    melody.insert(0, clef.TrebleClef())

    # Steps 3-5: MusicXML -> Verovio -> SVG
    return render_stream(melody)


def empty_staff_svg(composition):
    """An empty staff for a piece with no notes yet (NTT-55).

    Shows the clef, key signature, time signature and tempo the user picked,
    in one empty bar, so a new piece already looks like sheet music.
    """
    settings = composition_to_stream(composition)  # no notes: only key, time and tempo
    settings.insert(0, clef.TrebleClef())

    # Put the settings in one bar. A bare stream with no notes has nothing to export.
    bar = stream.Measure(number=1)
    for item in list(settings.getElementsByOffset(0)):
        bar.insert(0, item)

    return render_stream(stream.Part([bar]))


def render_stream(music):
    """Draw a music21 Stream as SVG with Verovio."""

    # Step 3: Export the Stream as MusicXML
    musicxml = GeneralObjectExporter(music).parse().decode("utf-8")

    # Step 4: Load MusicXML into Verovio
    toolkit = verovio.toolkit(False)
    toolkit.setResourcePath(VEROVIO_RESOURCES)
    toolkit.setOptions({"inputFrom": "xml", **DISPLAY_OPTIONS})

    if not toolkit.loadData(musicxml):
        raise ValueError("Could not load MusicXML into Verovio")

    # Step 5: Render the first page as SVG
    svg = toolkit.renderToSVG(1)

    if not svg or "<svg" not in svg:
        raise ValueError("Could not generate SVG")

    return svg
