def convert_solfege_chord_to_anglo_saxon(chord):
    solfege_to_anglo_saxon = {
        "DO": "C",
        "RE": "D",
        "MI": "E",
        "FA": "F",
        "SOL": "G",
        "LA": "A",
        "SI": "B"
    }

    for latin_note, anglo_saxon_note in solfege_to_anglo_saxon.items():
        if latin_note in chord:
            chord = chord.replace(latin_note, anglo_saxon_note)
    return chord
