

from music21 import key, meter, note as music_note
from music21 import pitch, stream, tempo



def composition_to_stream(composition):
    melody = stream.Stream()

    # Add key signature
    key_name = getattr(composition, "key_signature", None)
    current_key = None

    if key_name:
        tonic, mode = key_name.rsplit(" ", 1)
        tonic = key.convertKeyStringToMusic21KeyString(tonic)
        current_key = key.Key(tonic, mode)
        melody.insert(0, current_key)

    # Add time signature
    time_signature = getattr(composition, "time_signature", None)
    if time_signature:
        melody.insert(0, meter.TimeSignature(time_signature))

    # Add tempo
    bpm = getattr(composition, "tempo", None)
    if bpm is not None:
        melody.insert(0, tempo.MetronomeMark(number=bpm))

    # Keep notes in their saved order
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
                # Explicit choice: sharp, flat, or natural
                converted.pitch.accidental = pitch.Accidental(
                    item.accidental
                )
            elif current_key is not None:
                # Default choice: follow the current key
                key_accidental = current_key.accidentalByStep(
                    item.pitch
                )
                if key_accidental is not None:
                    converted.pitch.accidental = pitch.Accidental(
                        key_accidental.name
                    )

        converted.duration.type = item.duration
        melody.append(converted)

    return melody
