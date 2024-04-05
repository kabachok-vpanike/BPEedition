PITCH = {
    "Cb": 11, "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "E#": 5, "Fb": 4, "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "B#": 0, "c": 0, "d": 2,
    "e": 4, "f": 5, "g": 7, "a": 9, "b": 11
}

CHUNKS = [
    "sus4", "sus2", "sus", "XIX", "XIV", "IX", "IV", "XVIII", "XIII", "VIII", "III",
    "XVII", "XII", "VII", "II", "XVI", "XI", "VI", "I", "XV", "X", "V", "add#11",
    "add11+", "add+11", "add11", "add9-", "add-9", "add9+", "add+9", "add9", "add2",
    "add4", "add6", "add13-", "add-13", "addb13", "add13b", "add13", "69", "6/9", "#6",
    "maj13", "maj7", "maj9", "ma7", "+7", "7M", "maj", "M7", "2", "4", "b9", "-9", "+9",
    "*", "/#9", "/#11", "#11", "/#5", "#5", "/b13", "b13", "#9", "M9",
]

DIMINISHED_RELATED_NOTATIONS = ["min7b5", "m7b5", "m7-5", "7-5", "m5-", "m-5", "m75-", "5-", "maj7b5", "M7b5", "7b5",
                                "-5", "(b5)", "m(b5)", "dim7", "dim", "o", "°", "º"]
MINOR_RELATED_NOTATIONS = ["m", "M", "min", "mi"]
AUGMENTED_RELATED_NOTATIONS = ["aug", "+", "+5"]


def extract_chunk(chord, chunk):
    import re
    regex = re.compile(f"\\(?{re.escape(chunk)}\\)?")
    if regex.search(chord):
        return re.sub(regex, "", chord), True
    return chord, False


PitchClass = range(12)


class Chord:
    def __init__(self, root, bass, triad_quality, properties):
        self.root = root
        self.bass = bass
        self.triad_quality = triad_quality
        self.properties = properties


def parse_chord(chord):
    source_chord = chord
    properties = []
    bass = None
    root = None
    triad_quality = "major"

    if chord[:2] in PITCH:
        root = chord[:2]
        chord = chord[2:]
    elif chord[0] in PITCH:
        root = chord[0]
        chord = chord[1:]
    else:
        # print("    ROOT NOT FOUND")
        return None

    for chunk in CHUNKS:
        chord, extracted = extract_chunk(chord, chunk)
        if extracted:
            properties.append(chunk)

    if len(chord.split("/")) == 2:
        chord, bass_letter = chord.split("/")
        if bass_letter in PITCH:
            bass = PITCH[bass_letter]

    if chord in DIMINISHED_RELATED_NOTATIONS:
        triad_quality = "dim"
    elif chord in MINOR_RELATED_NOTATIONS:
        triad_quality = "minor"
    elif chord in ["m7+", "m#7"]:
        triad_quality = "minor"
        properties.append("maj7")
    elif chord in AUGMENTED_RELATED_NOTATIONS or chord in ["7+", "7+5"]:
        triad_quality = "aug"
        properties.append("7")
    elif chord == "m6":
        triad_quality = "minor"
        properties.append("6")
    elif chord == "m9":
        triad_quality = "minor"
        properties.append("9")
    elif chord == "m11":
        triad_quality = "minor"
        properties.append("11")
    elif chord == "m13":
        triad_quality = "minor"
        properties.append("7")
        properties.append("13")
    elif chord in ["m7", "min7"]:
        triad_quality = "minor"
        properties.append("m7")
    elif chord == "7":
        properties.append("7")
    elif chord == "9":
        properties.append("9")
        properties.append("7")
    elif chord == "11":
        properties.append("11")
        properties.append("7")
    elif chord == "13":
        properties.append("13")
        properties.append("7")
    elif chord == "5":
        properties.append("5")
    elif chord == "6":
        properties.append("6")
    elif chord == "3":
        properties.append("3")
    elif chord != "":
        if chord == "m#" and "m#" in source_chord:
            return parse_chord(source_chord.replace("m#", "#m"))
        # print("    NOT PARSED", chord, source_chord)
        return None

    return Chord(root, bass, triad_quality, properties)


def extract_chord_base(chord):
    parsed = parse_chord(chord)
    if parsed is None:
        return None
    extracted = parsed.root
    if parsed.triad_quality == 'minor':
        extracted += 'm'
    if '7' in parsed.properties:
        extracted += '7'

    return extracted


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
        parsed = extract_chord_base(ch)
        print(f"{ch}: {parsed}")
