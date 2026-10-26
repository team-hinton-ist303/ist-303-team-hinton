

from music21 import key, meter, note as music_note
from music21 import pitch, stream, tempo


def composition_to_stream(composition):
    melody = stream.Stream()

    # Add key signature
    key_name = getattr(composition, "key_signature", None)
    if key_name:
        tonic, mode = key_name.rsplit(" ", 1)
        tonic = key.convertKeyStringToMusic21KeyString(tonic)
        melody.insert(0, key.Key(tonic, mode))

    # Add time signature
    time_signature = getattr(composition, "time_signature", None)
    if time_signature:
        melody.insert(0, meter.TimeSignature(time_signature))

    # Add tempo
    bpm = getattr(composition, "tempo", None)
    if bpm is not None:
        melody.insert(0, tempo.MetronomeMark(number=bpm))

    # Read notes in their saved order
    ordered_notes = sorted(
        composition.notes,
        key=lambda item: item.position
    )

    for item in ordered_notes:
        if item.is_rest:
            converted = music_note.Rest()
        else:
            converted = music_note.Note(
                f"{item.pitch}{item.octave}"
            )

            if item.accidental:
                converted.pitch.accidental = pitch.Accidental(
                    item.accidental
                )

        converted.duration.type = item.duration
        melody.append(converted)

    return melody
