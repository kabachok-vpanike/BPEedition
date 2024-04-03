def extract_chord_base(chord):
    base = chord[0]
    if len(chord) > 1 and chord[1] in "#b":
        base += chord[1]
        chord = chord[2:]
    else:
        chord = chord[1:]

    if 'maj7' in chord:
        return base

    quality = ""
    seventh = ""

    if chord.startswith('m'):
        quality = "m"
        chord = chord[1:]

    if '7' in chord:
        seventh = "7"

    return f"{base}{quality}{seventh}"


if __name__ == "__main__":
    test_chords = [
        "C", "G", "Am", "E7", "Dm7", "G7", "Cmaj7", "F#m7(b5)", "Bb7", "A7sus4", "D#m",
        "G#maj7", "C#m7", "Fm", "Bb6", "Eaug", "Abm", "Db7", "Em9", "Am6", "Dadd9", "F#sus2",
        "Gsus4", "C7", "Bm7", "A#dim", "Gdim", "C#dim7", "Ebm", "F#7", "Bmaj7", "Em", "Aadd2",
        "Gm", "D#7", "Cm", "F7", "Ebmaj7", "Ab7", "Dbmaj7", "Gbm", "B7", "F#m", "Bbm", "Eb7",
        "Am7", "Dm", "E9", "G#7", "C#m", "F#dim", "Bdim", "Adim7", "D#m7", "A#m7(b5)", "Fm6",
        "C#7#9", "Bbadd9", "G#m6", "Ebm7", "F#11", "Cm6", "Am11", "Bm9", "G13", "D7#9", "A#7",
        "F#m9", "C#sus4", "Bbsus2", "G#dim", "Ebadd9", "Amaj7", "Dm6", "Fm9", "Abmaj7", "Dbm7",
        "Gbmaj7", "Bm6", "F#m6", "Bbm6", "Eb9", "A#m9", "D#dim7", "Asus2", "E7#9", "G#9",
        "C#11", "F#7(b9)", "Bb13", "Ebm9", "Absus4", "Dbadd9", "Gbm7", "B7#9", "F#m7#5",
        "Bbmaj7", "Eb13", "A#dim7", "D#sus4", "Gm7", "Cm9", "F11", "Ab13", "Db13"
    ]

    test_chords2 = [
        "Cmaj7#11", "Amsus4", "G7sus4", "F#m9", "Bb13#11", "Am11(b9)", "C#7#9(b13)", "Ebmaj9", "Abm6/9", "G#7b9",
        "F(add9)", "Dm6/9", "G13sus4", "A/C#", "F#m7b5", "Bb6add9", "C/G", "E7#9#5", "Dbmaj7#11", "Am6add9",
        "Gbm13", "B7alt", "E9sus", "Ab7#11", "D#m7#5", "G#m(b5)", "Cm(maj7)", "F7#5(b9)", "A#dim7", "Dadd4",
        "Gm7b5", "Bmaj9#11", "Eb7add13", "A7b9b13", "F#7alt", "C#m9", "Bbm7b5", "Ebm6", "Am/G", "D7#11",
        "G#maj9", "Fm11", "Db13#11", "A#m7#5", "D#sus2", "Gadd9", "Bm7b5", "E7b9#9", "Abmaj7#5", "Dmaj7#9#11",
        "Gbm7#5", "B7#5#9", "Em11b9", "A#11", "F#m11", "C#7(b9#5)", "Bbmaj9#11", "Eb13(b9)", "Am7#5", "Dm(add11)",
        "G#13", "F#7b9#11", "Dbm7b5", "A#m9", "Ddim7", "Gm9", "Badd9", "Ebm9#11", "Absus2", "D#7#11",
        "Gb7#9", "Bm6add9", "E11", "Abm7", "D#m9", "G7#5#9", "Fm6/9", "C#maj9", "Bb7b5", "Ebm7#9",
        "Am9#11", "D7sus4b9", "G#m7#5", "F#add9", "Db7#5", "A#m6", "Dmaj13", "Gbm9", "B7b9#9", "E7add13",
        "Ab7b9", "D#maj7#5", "Gm(add13)", "F13#11", "Cmaj13", "Bbm9", "E#m7", "A7#5", "D#m11", "G#sus4b9",
        "F#m13", "C#add9", "Bbm6/9", "Ebadd9", "A13b9", "Dm9", "G#11", "F#7#5", "C#m7b5", "Badd11",
        "Em7#5", "A#7#9", "D#add9", "Gbsus2", "Fm7#11", "C7b9#9", "Bm9#11", "Eb7#5", "Aminmaj7", "D#7sus4"
    ]
    for ch in test_chords2:
        print(f"{ch}: {extract_chord_base(ch)}")
