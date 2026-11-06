import os
import xml.etree.ElementTree as ET
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



def prepare_note_ids(musicxml):
    """Give exported segments unique IDs linked to their database note."""
    root = ET.fromstring(musicxml)
    lookup = {}
    counts = {}

    for element in root.iter("note"):
        identifier = element.get("id", "")
        prefix = "db-note-"
        if not identifier.startswith(prefix):
            continue

        note_id = identifier[len(prefix):]
        if not note_id.isdecimal():
            continue

        counts[note_id] = counts.get(note_id, 0) + 1
        segment_id = f"db-note-{note_id}-segment-{counts[note_id]}"
        element.set("id", segment_id)
        lookup[segment_id] = note_id

    return ET.tostring(root, encoding="unicode"), lookup


def annotate_note_ids(svg, lookup):
    """Attach database IDs to selectable SVG note and rest elements."""
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    root = ET.fromstring(svg)

    for element in root.iter():
        classes = set(element.get("class", "").split())
        if not classes.intersection({"note", "rest", "mRest"}):
            continue
        note_id = lookup.get(element.get("id"))
        if note_id is not None:
            element.set("data-note-id", note_id)

    return ET.tostring(root, encoding="unicode")


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
    musicxml, note_lookup = prepare_note_ids(musicxml)

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

    return annotate_note_ids(svg, note_lookup)
