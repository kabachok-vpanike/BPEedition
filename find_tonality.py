from transpose_chord import get_all_transpositions, extract_root
from transpose_chord import transpose_chord

note_values = {
    'C': 0, 'B#': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4,
    'F': 5, 'E#': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11
}

weights = {'C': 2, 'Am': 2,
           'Dm': 1, 'E': 1, 'Em': 1, 'F': 1, 'G': 1,
           'D': 0.5, 'B7': 0.5, 'A7': 0.5, 'E7': 0.5, 'G7': 0.5}


def are_equivalent(note1, note2):
    root1, quality1 = extract_root(note1)
    root2, quality2 = extract_root(note2)
    return note_values[root1] == note_values[root2] and quality1 == quality2


def count_score_for_one_sequence(sequence):
    return sum(weights.get(element, 0) for element in sequence)


def get_top_3_score_pairs(chord_sequence):
    scores = [(transposed_chords, count_score_for_one_sequence(transposed_chords[0])) for transposed_chords in
              get_all_transpositions(chord_sequence)]
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return sorted_scores[:3]


def find_tonality(chord_sequence):
    res = []
    max_pairs = get_top_3_score_pairs(chord_sequence)
    for pair in max_pairs:
        res.append([transpose_chord('C', -pair[0][1]), transpose_chord('Am', -pair[0][1])])
    return res
