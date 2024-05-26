import math

from find_tonality import TonalityFinder, are_equivalent
from transpose_chord import get_all_transpositions, transpose_chord


class TonalityWithQualityFinder:
    def __init__(self, songs_array, test_array, minor_weights=None, major_weights=None):
        self.songs_array = songs_array.copy()
        self.test_array = test_array.copy()
        if (minor_weights is None or major_weights is None) and not (TonalityFinder.every_chord_has_a_key(songs_array)):
            raise Exception("There must be either weights provided or a song_array with a key for each song")
        if minor_weights is None or major_weights is None:
            calculated_weights = self.precalculate_weights(songs_array)
            self.major_weights = calculated_weights["weights_for_major"]
            self.minor_weights = calculated_weights["weights_for_minor"]
        else:
            self.major_weights = major_weights
            self.minor_weights = minor_weights

    @staticmethod
    def precalculate_weights(songs_array):
        songs_array_minor = [song for song in songs_array if song['key'].endswith('m')]
        songs_array_major = [song for song in songs_array if not song['key'].endswith('m')]

        weights_for_minor = TonalityFinder.precalculate_weights(songs_array_minor)
        weights_for_major = TonalityFinder.precalculate_weights(songs_array_major)
        print("major and minor:")
        print(sorted(weights_for_major.items(), key=lambda x: x[1], reverse=True),
              sorted(weights_for_minor.items(), key=lambda x: x[1], reverse=True))
        return {"weights_for_minor": weights_for_minor, "weights_for_major": weights_for_major}

    @staticmethod
    def entropy_score(sequence, chords_weights):
        entropy = -sum(chords_weights.get(chord, 0) * math.log(chords_weights.get(chord, 1e-9)) for chord in sequence)
        return entropy

    @staticmethod
    def count_score_for_one_sequence(sequence, major_weights, minor_weights):
        return {"major_score": sum(major_weights.get(element, 0) for element in sequence),
                "minor_score": sum(minor_weights.get(element, 0) for element in sequence)}

    def get_top_3_score_guess(self, chord_sequence, major_weights, minor_weights):
        scores = []
        for transposed_chords in get_all_transpositions(chord_sequence=chord_sequence):
            major_and_minor_scores = self.count_score_for_one_sequence(sequence=transposed_chords[0],
                                                                       minor_weights=minor_weights,
                                                                       major_weights=major_weights)
            scores.append(({"transposed_chords": transposed_chords[0], "semitones_up": transposed_chords[1],
                            "score": major_and_minor_scores["major_score"],
                            "quality": "major"}))
            scores.append(({"transposed_chords": transposed_chords[0], "semitones_up": transposed_chords[1],
                            "score": major_and_minor_scores["minor_score"],
                            "quality": "minor"}))
        sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:3]

    def find_tonality(self, chord_sequence, major_weights=None, minor_weights=None):
        res = []
        max_guesses = self.get_top_3_score_guess(chord_sequence=chord_sequence,
                                                 major_weights=self.major_weights
                                                 if major_weights is None else major_weights,
                                                 minor_weights=self.minor_weights
                                                 if minor_weights is None else minor_weights)
        for guess in max_guesses:
            base_note = 'C'
            if guess["quality"] == "minor":
                base_note = 'Am'
            res.append(transpose_chord(base_note, -guess["semitones_up"]))
        return res

    def success_rate(self, test_chords, major_weights, minor_weights):
        success_guesses = 0
        for one_song in test_chords:
            guesses = self.find_tonality(chord_sequence=one_song["chords"], minor_weights=minor_weights,
                                         major_weights=major_weights)[:2]
            for guess in guesses:
                if are_equivalent(guess, one_song["key"]):
                    success_guesses += 1
                    break
        print('\n\n')
        return success_guesses / len(test_chords)

    def find_tonality_multiple_iterations(self, songs_array, minor_weights=None, major_weights=None, step=0):
        chord_frequency = {"minor": {}, "major": {}}
        minor_weights = minor_weights.copy() if minor_weights is not None else self.minor_weights.copy()
        major_weights = major_weights.copy() if major_weights is not None else self.major_weights.copy()
        old_weights = {"major": major_weights.copy(), "minor": minor_weights.copy()}
        number_of_songs = {"major": 0, "minor": 0}
        for chord_sequence in songs_array:
            try:
                best_fits = \
                    self.get_top_3_score_guess(chord_sequence=chord_sequence['chords'], minor_weights=minor_weights,
                                               major_weights=major_weights)[:1]
                for best_fit in best_fits:
                    quality = best_fit["quality"]
                    number_of_songs[quality] += 1
                    for chord in set(best_fit["transposed_chords"]):
                        chord_frequency[quality][chord] = chord_frequency[quality].get(chord, 0) + 1
            except Exception:
                print(chord_sequence['chords'])
                raise Exception("aaaa")

        weights = {"major": {}, "minor": {}}
        for quality in ["major", "minor"]:
            for chord in chord_frequency[quality]:
                percent = chord_frequency[quality][chord] / number_of_songs[quality]
                if percent > 0.01:
                    weights[quality][chord] = round(chord_frequency[quality][chord] / number_of_songs[quality], 3)

        print(f"step {step}: ", dict(sorted(weights["major"].items(), key=lambda item: item[1], reverse=True)))
        print(f"step {step}: ", dict(sorted(weights["minor"].items(), key=lambda item: item[1], reverse=True)))
        print(
            f"success rate for test: {self.success_rate(test_chords=self.test_array, major_weights=weights["major"],
                                                        minor_weights=weights["minor"])}")
        if not (weights["major"] == old_weights["major"] and weights["minor"] == old_weights["minor"]):
            self.find_tonality_multiple_iterations(songs_array=songs_array, major_weights=weights["major"],
                                                   minor_weights=weights["minor"], step=step + 1)
        return weights
