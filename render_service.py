import xml.etree.ElementTree as ET


import verovio

from music21 import clef
from music21.musicxml.m21ToXml import GeneralObjectExporter
from music_stream import composition_to_stream



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

    # Step 3: Export the Stream as MusicXML
    musicxml = GeneralObjectExporter(melody).parse().decode("utf-8")
    musicxml, note_lookup = prepare_note_ids(musicxml)

    # Step 4: Load MusicXML into Verovio
    toolkit = verovio.toolkit()
    toolkit.setOptions({"inputFrom": "xml"})

    if not toolkit.loadData(musicxml):
        raise ValueError("Could not load MusicXML into Verovio")

    # Step 5: Render the first page as SVG
    svg = toolkit.renderToSVG(1)

    if not svg or "<svg" not in svg:
        raise ValueError("Could not generate SVG")

    return annotate_note_ids(svg, note_lookup)
