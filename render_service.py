
import verovio

from music21 import clef
from music21.musicxml.m21ToXml import GeneralObjectExporter
from music_stream import composition_to_stream


def composition_to_svg(composition):
    """Convert a database composition into sheet music SVG."""

    # Step 1: Convert database notes to a music21 Stream
    melody = composition_to_stream(composition)

    # An empty composition uses a placeholder in the UI
    if not list(melody.notesAndRests):
        return ""

    # Step 2: Add a treble clef
    melody.insert(0, clef.TrebleClef())

    # Step 3: Export the Stream as MusicXML
    musicxml = GeneralObjectExporter(melody).parse().decode("utf-8")

    # Step 4: Load MusicXML into Verovio
    toolkit = verovio.toolkit()
    toolkit.setOptions({"inputFrom": "xml"})

    if not toolkit.loadData(musicxml):
        raise ValueError("Could not load MusicXML into Verovio")

    # Step 5: Render the first page as SVG
    svg = toolkit.renderToSVG(1)

    if not svg or "<svg" not in svg:
        raise ValueError("Could not generate SVG")

    return svg
