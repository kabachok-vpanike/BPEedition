def extract_root(chord):
    root = chord[0].upper()
    if len(chord) > 1 and chord[1] in "#b":
        root += chord[1]
        quality = chord[2:]
    else:
        quality = chord[1:]
    return root, quality


transpose_up = {
    "C": "C#", "C#": "D", "Db": "D", "D": "D#", "D#": "E", "Eb": "E", "E": "F",
    "F": "F#", "F#": "G", "Gb": "G", "G": "G#", "G#": "A", "Ab": "A", "A": "A#",
    "A#": "B", "Bb": "B", "B": "C", "B#": "C#", "Cb": "B"
}

transpose_down = {
    "C": "B", "C#": "C", "Db": "C", "D": "Db", "D#": "D", "Eb": "D", "E": "Eb",
    "F": "E", "F#": "F", "Gb": "F", "G": "Gb", "G#": "G", "Ab": "G", "A": "Ab",
    "A#": "A", "Bb": "A", "B": "Bb", "B#": "C", "Cb": "B"
}


def transpose_chord_up(chord):
    root, quality = extract_root(chord)
    new_root = transpose_up[root]
    return new_root + quality


def transpose_chord(chord, semitones):
    total_semitones = 12
    if semitones < 0:
        semitones = total_semitones + semitones
    for _ in range(semitones % total_semitones):
        chord = transpose_chord_up(chord)
    return chord


def get_all_transpositions(chord_sequence):
    all_sequence_transpositions = [(chord_sequence, 0)]
    for semitones_number in range(1, 12):
        all_sequence_transpositions.append(
            ([transpose_chord(chord, semitones_number) for chord in chord_sequence], semitones_number))
    return all_sequence_transpositions


if __name__ == "__main__":

    test_chords = [
        "C",
        "Cm",
        "C7",
        "C#",
        "C#m",
        "C#7",
        "Db",
        "Dbm",
        "Db7",
        "E",
        "Eb",
        "Ebm",
        "F",
        "Fm",
        "F7",
        "B",
        "Bm",
        "B7",
        "Bb",
        "Bbm",
        "Bb7",
        "A#",
        "A#m",
        "A#7",
    ]

    for ch in test_chords:
        up = transpose_chord_up(ch)
        print(f"{ch}: Up -> {up}")
