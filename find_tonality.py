from transpose_chord import get_all_transpositions, extract_root
from extract_base import extract_chord_base
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


def are_equivalent(note1, note2):
    root1, quality1 = extract_root(note1)
    root2, quality2 = extract_root(note2)
    return note_values[root1] == note_values[root2] and quality1 == quality2


def semitones_up_distance_from_unsigned_tonality(chord):
    base_tonality = 'C'
    if 'm' in extract_chord_base(chord):
        base_tonality = 'Am'
    semitones_number = 0
    while not are_equivalent(transpose_chord(base_tonality, semitones_number), chord):
        semitones_number += 1
    return semitones_number


def transpose_to_unsigned_tonality(chords, key):
    distance_up = semitones_up_distance_from_unsigned_tonality(key)
    return [transpose_chord(chord, -distance_up) for chord in chords]


class TonalityFinder:
    def __init__(self, songs_array, test_array, weights=None):
        self.songs_array = songs_array.copy()
        self.test_array = test_array.copy()
        if weights is None and not (self.every_chord_has_a_key(songs_array)):
            raise Exception("There must be either weights provided or a song_array with a key for each song")
        self.weights = weights if weights is not None else self.precalculate_weights(songs_array)

    @staticmethod
    def every_chord_has_a_key(songs_array):
        for song in songs_array:
            if not ("key" in song and ("chords" in song or "initial_chords" in song)):
                print(song)
                return False
        return True

    @staticmethod
    def precalculate_weights(songs_array):
        chords_frequency = {}
        for chords_plus_key in songs_array:
            chords_in_unsigned_tonality = transpose_to_unsigned_tonality(chords=chords_plus_key["chords"],
                                                                         key=chords_plus_key["key"])
            for chord in set(chords_in_unsigned_tonality):
                chords_frequency[chord] = chords_frequency.get(chord, 0) + 1
        weights = {}
        for chord in chords_frequency:
            weights[chord] = round(chords_frequency[chord] / len(songs_array), 3)
        print(sorted(weights.items(), key=lambda x: x[1], reverse=True))
        return weights

    @staticmethod
    def count_score_for_one_sequence(sequence, weights):
        return sum(weights.get(element, 0) for element in sequence)

    def get_top_3_score_pairs(self, chord_sequence, weights):
        scores = [(transposed_chords, self.count_score_for_one_sequence(sequence=transposed_chords[0], weights=weights))
                  for transposed_chords in
                  get_all_transpositions(chord_sequence=chord_sequence)]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return sorted_scores[:3]

    def find_tonality(self, chord_sequence, weights=None):
        res = []
        max_pairs = self.get_top_3_score_pairs(chord_sequence=chord_sequence,
                                               weights=self.weights if weights is None else weights)
        for pair in max_pairs:
            res.append([transpose_chord('C', -pair[0][1]), transpose_chord('Am', -pair[0][1])])
        return res

    def find_tonality_multiple_iterations(self, songs_array, weights=None, step=0):
        chords_frequency = {}
        weights = weights.copy() if weights is not None else self.weights.copy()
        old_weights = weights.copy()
        for chord_sequence in songs_array:
            try:
                best_fit = self.get_top_3_score_pairs(chord_sequence=chord_sequence['chords'], weights=weights)[0][0][0]
                for chord in set(best_fit):
                    chords_frequency[chord] = chords_frequency.get(chord, 0) + 1
            except Exception:
                print(chord_sequence['chords'])
                raise Exception("aaaa")

        weights = {}
        for chord in chords_frequency:
            percent = chords_frequency[chord] / len(songs_array)
            if percent > 0.01:
                weights[chord] = round(chords_frequency[chord] / len(songs_array), 3)
        print(f"step {step}: ", dict(sorted(weights.items(), key=lambda item: item[1], reverse=True)))
        print(f"success rate for test: {self.success_rate(test_chords=self.test_array, weights=weights)}")
        if old_weights != weights:
            self.find_tonality_multiple_iterations(songs_array=songs_array, weights=weights, step=step + 1)
        return weights

    def success_rate(self, test_chords, weights):
        success_guesses = 0
        for one_song in test_chords:
            pair_guesses = self.find_tonality(chord_sequence=one_song["chords"], weights=weights)[:2]
            for pair in pair_guesses:
                if are_equivalent(pair[0], one_song["key"]) or are_equivalent(pair[1], one_song["key"]):
                    success_guesses += 1
                    break
        return success_guesses / len(test_chords)


if __name__ == "__main__":
    assert transpose_to_unsigned_tonality(
        ["Em", "Am", "Bm", "G", "C", "D", "E7", "F#m7b5", "Gmaj7", "A7", "B7", "Cmaj7"], 'Em'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "A7", "Bm7b5", "Cmaj7", "D7", "E7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["Dm", "Gm", "Am", "F", "Bb", "C", "D7", "E7", "Fmaj7", "Gm7", "Am7", "Bbmaj7"], 'Dm'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "A7", "B7", "Cmaj7", "Dm7", "Em7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["Bm", "Em", "F#m", "D", "G", "A", "Bm7", "C#7", "Dmaj7", "Em7", "F#m7", "Gmaj7"], 'Bm'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "Am7", "B7", "Cmaj7", "Dm7", "Em7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["Gm", "Cm", "Dm", "Bb", "Eb", "F", "Gm7", "A7", "Bbmaj7", "Cm7", "Dm7", "Ebmaj7"], 'Gm'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "Am7", "B7", "Cmaj7", "Dm7", "Em7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["F#m", "Bm", "C#m", "A", "D", "E", "F#m7", "G#7", "Amaj7", "Bm7", "C#m7", "Dmaj7"], 'F#m'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "Am7", "B7", "Cmaj7", "Dm7", "Em7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["C#m", "F#m", "G#m", "E", "A", "B", "C#m7", "D#7", "Emaj7", "F#m7", "G#m7", "Amaj7"], 'C#m'
    ) == ["Am", "Dm", "Em", "C", "F", "G", "Am7", "B7", "Cmaj7", "Dm7", "Em7", "Fmaj7"]

    assert transpose_to_unsigned_tonality(
        ["G", "C", "D", "Em", "Am", "Bm", "G7", "A7", "Bm7", "Cmaj7", "D7", "Em7"], 'G'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]

    assert transpose_to_unsigned_tonality(
        ["D", "G", "A", "Bm", "Em", "F#m", "D7", "E7", "F#m7", "Gmaj7", "A7", "Bm7"], 'D'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]

    assert transpose_to_unsigned_tonality(
        ["A", "D", "E", "F#m", "Bm", "C#m", "A7", "B7", "C#m7", "Dmaj7", "E7", "F#m7"], 'A'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]

    assert transpose_to_unsigned_tonality(
        ["E", "A", "B", "C#m", "F#m", "G#m", "E7", "F#7", "G#m7", "Amaj7", "B7", "C#m7"], 'E'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]

    assert transpose_to_unsigned_tonality(
        ["B", "E", "F#", "G#m", "C#m", "D#m", "B7", "C#7", "D#m7", "Emaj7", "F#7", "G#m7"], 'B'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]

    assert transpose_to_unsigned_tonality(
        ["F", "Bb", "C", "Dm", "Gm", "Am", "F7", "G7", "Am7", "Bbmaj7", "C7", "Dm7"], 'F'
    ) == ["C", "F", "G", "Am", "Dm", "Em", "C7", "D7", "Em7", "Fmaj7", "G7", "Am7"]
