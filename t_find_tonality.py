import json
from collections import Counter, defaultdict

from extract_base import extract_chord_base
from unknown_chords_utils import convert_solfege_chord_to_anglo_saxon
from find_tonality import transpose_to_unsigned_tonality
from chords_counter import count_chord_frequencies

major_weights = {'F': 0.968, 'C': 0.942, 'G': 0.913, 'Am': 0.696, 'Dm': 0.385, 'Em': 0.269, 'D': 0.239, 'E': 0.159,
                 'A#': 0.152, 'A': 0.141, 'G7': 0.117, 'D#': 0.079, 'G#': 0.075, 'Fm': 0.071, 'C7': 0.07, 'D7': 0.062,
                 'Gm': 0.055, 'E7': 0.053, 'B': 0.052, 'Bm': 0.047, 'F#': 0.045, 'Cm': 0.038, 'C#': 0.036, 'A7': 0.027,
                 'F7': 0.023, 'F#m': 0.018, 'Bb': 0.016, 'A#m': 0.016, 'D#m': 0.012}

minor_weights = {'Dm': 0.948, 'Am': 0.898, 'C': 0.683, 'F': 0.675, 'G': 0.59, 'E': 0.388, 'Em': 0.304, 'E7': 0.26,
                 'A': 0.192, 'D': 0.166, 'G7': 0.159, 'A7': 0.154, 'A#': 0.133, 'Gm': 0.113, 'B': 0.088, 'Bm': 0.077,
                 'Fm': 0.071, 'D7': 0.059, 'C7': 0.058, 'F#': 0.055, 'G#': 0.055, 'B7': 0.053, 'D#': 0.05, 'C#': 0.043,
                 'Cm': 0.043, 'F7': 0.042, 'F#m': 0.035, 'D#m': 0.033, 'A#m': 0.03, 'C#m': 0.023, 'A#7': 0.021,
                 'G#m': 0.02, 'F#7': 0.016, 'Bb': 0.016, 'G#7': 0.013}

artist_to_number_of_songs = defaultdict(lambda: defaultdict(int))


def get_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def remove_consecutive_duplicates(strings):
    if not strings or len(strings) == 1:
        return strings

    result = [strings[0]]

    for i in range(1, len(strings)):
        if strings[i] != strings[i - 1]:
            result.append(strings[i])

    return result


def dataset_to_key_and_chords(songs_array):
    simplified = []
    for index, one_song in enumerate(songs_array):
        if index % 10000 == 0:
            print(index)
        chords = remove_consecutive_duplicates(
            list(map(lambda x: extract_chord_base(convert_solfege_chord_to_anglo_saxon(x)),
                     one_song[3].split())))
        if None not in chords:
            simplified.append({
                "artist": one_song[4],
                "title": one_song[5],
                "key": one_song[6],
                "initial_chords": one_song[3],
                "simplified_chords": chords
            })

    return simplified


def add_key_to_songs(songs_array, tonality_with_quality_finder, major_weights, minor_weights):
    step = 0
    for one_song in songs_array:
        step += 1
        if step % 10000 == 0:
            print(step)
        if one_song['key'] is None:
            one_song['key'] = \
                tonality_with_quality_finder.find_tonality(
                    chord_sequence=one_song['chords'],
                    minor_weights=minor_weights,
                    major_weights=major_weights)[0]
        one_song['transposed_to_unsigned'] = transpose_to_unsigned_tonality(
            chords=one_song['chords'],
            key=convert_solfege_chord_to_anglo_saxon(
                one_song['key'].replace('С', 'C')))
        quality = "minor" if one_song['key'].endswith('m') else "major"
        artist_to_number_of_songs[quality][one_song['artist']] += 1
    return songs_array


def count_most_frequent_artists(data, n=300):
    artists = [item[4] for item in data if
               item[4] and 'Misc' not in item[4] and 'песни' not in item[4].casefold()]
    artist_counts = Counter(artists)
    most_common = artist_counts.most_common(n)
    most_common_artist_names = [artist for artist, count in most_common]
    return most_common_artist_names


def count_most_frequent_chords(songs_array, frequent_artists, max_sequence_length):
    def merge_chord_counts(old, new):
        for key, count in new.items():
            old[key] += count
        return old

    def to_plain_dict(d):
        if isinstance(d, (defaultdict, Counter)):
            d = {k: to_plain_dict(v) for k, v in d.items()}
        return d

    from_artist_to_frequent_chords = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    for one_song in songs_array:
        if one_song['artist'] in frequent_artists:
            artist_name = one_song['artist']
            new_value = count_chord_frequencies(chords=one_song['transposed_to_unsigned'],
                                                max_sequence_length=max_sequence_length)
            quality = "minor" if one_song['key'].endswith('m') else "major"
            for seq_length, chords_counter in new_value.items():
                from_artist_to_frequent_chords[artist_name][quality][seq_length] = merge_chord_counts(
                    from_artist_to_frequent_chords[artist_name][quality][seq_length], chords_counter)

                from_artist_to_frequent_chords[artist_name]['all'][seq_length] = merge_chord_counts(
                    from_artist_to_frequent_chords[artist_name]['all'][seq_length], chords_counter)
    return to_plain_dict(from_artist_to_frequent_chords)


def find_song_with_most_chords_occurrences(songs_array, artist_name, chord_sequence, quality):
    chord_sequence = list(chord_sequence)

    best_entry = None
    max_occurrences = 0

    for entry in songs_array:
        entry_quality = "minor" if entry['key'].endswith('m') else "major"
        if entry['artist'] == artist_name and entry_quality == quality:
            occurrences = sum(1 for i in range(len(entry['transposed_to_unsigned']) - len(chord_sequence) + 1)
                              if entry['transposed_to_unsigned'][i:i + len(chord_sequence)] == chord_sequence)

            if occurrences > max_occurrences:
                max_occurrences = occurrences
                best_entry = entry

    return best_entry, max_occurrences


def count_minor_major_songs(annotated):
    for song in annotated:
        key = 'major'
        if song['key'].endswith('m'):
            key = 'minor'
        artist_to_number_of_songs[key][song['artist']] += 1
        artist_to_number_of_songs['all'][song['artist']] += 1


if __name__ == '__main__':
    unknown_chords = ['N.С.', 'N.C.', '¤', 'R', ']A5', 'S', 'H', '%', '2', '`', '`_´', '*', '(', 'h', '\x1aC', 'L', '(',
                      '`', 'N', 'С', '57', 'INTERMEDIO', '022000', '[Am Bbm]', 'С#', 'M', 'Intro', '[D# E]', 'hm', 'ho',
                      '(no3)', 'N.C', '*E', '(A)', '(C)', '\\Am', 'В', 'Вm', 'Pre-coro', '(D', '*Am', '[Bb5/F C5/G]',
                      "'Amaj7", 'M', 'Ñ\x84', ',Dadd9', '9', 'nc', '(G)', 'hammer', 'Аb', '(A)', '?', '(Fsus4)',
                      'F\u202d#',
                      'А#', '(Fsus4)', ',Eb', '*Asus2', '[F#7 G7]', 'JESÚS', '12', '557765', '557765', '`Am9']  # 🙏

    muzland_songs = get_json('muzland.json')

    train = dataset_to_key_and_chords(muzland_songs[:2000])
    test = dataset_to_key_and_chords(muzland_songs[2000:])

    whole_dataset_json = get_json('exported-chords.json')
    most_frequent_artists = (count_most_frequent_artists(whole_dataset_json))
    print(len(whole_dataset_json))
    # whole_dataset_json = [subarray for subarray in whole_dataset_json if subarray[4] in most_frequent_artists]
    print(len(whole_dataset_json))
    # whole_dataset = dataset_to_key_and_chords(whole_dataset_json)

    # tf = TonalityFinder(songs_array=train, test_array=test)
    # tonalityWithQualityFinder = TonalityWithQualityFinder(songs_array=train, test_array=test)
    # revised_weights = tonalityWithQualityFinder.find_tonality_multiple_iterations(songs_array=whole_dataset)
    # print("revised:", revised_weights)
    # print(tf.success_rate(test_chords=test, weights=tf.weights))
    # revised_weights = tf.find_tonality_multiple_iterations(whole_dataset)

    annotated = get_json('annotated-exported-chords.json')
    count_minor_major_songs(annotated)
    # annotated = add_key_to_songs(songs_array=whole_dataset, tonality_with_quality_finder=tonalityWithQualityFinder,
    #                            major_weights=major_weights, minor_weights=minor_weights)

    most_frequent_chords_for_most_frequent_artists = count_most_frequent_chords(songs_array=annotated,
                                                                                frequent_artists=most_frequent_artists,
                                                                                max_sequence_length=4)


    def convert(data):
        artists_no_quality = set()
        data = data.copy()
        for artist in data:
            for quality in data[artist]:
                for length in data[artist][quality]:
                    chord_data = data[artist][quality][length]
                    new_chord_data = {}
                    for chords, count in chord_data.items():
                        new_key = json.dumps(list(chords))
                        if artist_to_number_of_songs[quality][artist] == 0:
                            artists_no_quality.add(artist)
                            new_chord_data[new_key] = 0
                        else:
                            new_chord_data[new_key] = count / artist_to_number_of_songs[quality][artist]
                    data[artist][quality][length] = new_chord_data
        # json_data = json.dumps(data, ensure_ascii=False)
        print(artists_no_quality)
        return data


    file_path = 'MostFrequentChords.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(convert(most_frequent_chords_for_most_frequent_artists), file, ensure_ascii=False)

    # with open("output.txt", "w") as f:
    #     for artist, frequencies in most_frequent_chords_for_most_frequent_artists.items():
    #         print(artist, ":\n", file=f)
    #         for quality, length_chord_and_frequency in frequencies.items():
    #             # print(quality, length_chord_and_frequency)
    #             # print(" quality:", quality, file=f)
    #             total_number_of_songs = 0
    #             for q in ["major", "minor"]:
    #                 total_number_of_songs += artist_to_number_of_songs[q][artist]
    #             print(
    #                 f" {quality} songs number: {artist_to_number_of_songs[quality][artist]} "
    #                 f"({round(artist_to_number_of_songs[quality][artist] / total_number_of_songs * 100, 2)}%)",
    #                 file=f)
    #             for length, chord_and_frequency in length_chord_and_frequency.items():
    #                 print("  length of chords sequence: ",
    #                       length, file=f)
    #                 if artist_to_number_of_songs[quality][artist] == 0:
    #                     continue
    #                 # print(chord_and_frequency)
    #                 for chord, frequency in (
    #                         sorted(chord_and_frequency.items(), key=lambda x: x[1], reverse=True)):
    #                     if frequency < 5:
    #                         continue
    #                     print("   ", *chord, '—', frequency,
    #                           f"({round(frequency / artist_to_number_of_songs[quality][artist] * 100, 2)}%)", file=f,
    #                           end='\t\t')
    #                     most_representing, occurrences = find_song_with_most_chords_occurrences(songs_array=whole_dataset,
    #                                                                                             artist_name=artist,
    #                                                                                             chord_sequence=chord,
    #                                                                                             quality=quality)
    #                     print(f"({occurrences}) {most_representing['title']} {most_representing['transposed_to_unsigned']}",
    #                           file=f)
    #                 print(file=f)
    #         print('\n', file=f)
    # for i in annotated:
    #    print(i['transposed_to_unsigned'])
    #    counted = count_chord_frequencies(chords=i['transposed_to_unsigned'], max_sequence_length=3)
    #    for j in counted:
    #        print(sorted(counted[j].items(), key=lambda x: x[1], reverse=True), '\n')
