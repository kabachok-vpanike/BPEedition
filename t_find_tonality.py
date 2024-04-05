import json
from extract_base import extract_chord_base
from find_tonality import TonalityFinder
from unknown_chords_utils import convert_solfege_chord_to_anglo_saxon
import traceback


# weights = {'C': 2, 'Am': 2,
#           'Dm': 1, 'E': 1, 'Em': 1, 'F': 1, 'G': 1,
#           'D': 0.5, 'B7': 0.5, 'A7': 0.5, 'E7': 0.5, 'G7': 0.5}

def get_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def dataset_to_key_and_chords(songs_array):
    simplified = []

    for index, one_song in enumerate(songs_array):
        if index % 10000 == 0:
            print(index)
        chords = list(map(lambda x: extract_chord_base(convert_solfege_chord_to_anglo_saxon(x)), one_song[3].split()))
        if None not in chords:
            simplified.append({
                "key": one_song[6],
                "chords": chords
            })

    return simplified


unknown_chords = ['N.С.', 'N.C.', '¤', 'R', ']A5', 'S', 'H', '%', '2', '`', '`_´', '*', '(', 'h', '\x1aC', 'L', '(',
                  '`', 'N', 'С', '57', 'INTERMEDIO', '022000', '[Am Bbm]', 'С#', 'M', 'Intro', '[D# E]', 'hm', 'ho',
                  '(no3)', 'N.C', '*E', '(A)', '(C)', '\\Am', 'В', 'Вm', 'Pre-coro', '(D', '*Am', '[Bb5/F C5/G]',
                  "'Amaj7", 'M', 'Ñ\x84', ',Dadd9', '9', 'nc', '(G)', 'hammer', 'Аb', '(A)', '?', '(Fsus4)', 'F\u202d#',
                  'А#', '(Fsus4)', ',Eb', '*Asus2', '[F#7 G7]', 'JESÚS', '12', '557765', '557765', '`Am9']  # 🙏

muzland_songs = get_json('muzland.json')

train = dataset_to_key_and_chords(muzland_songs[:2000])
test = dataset_to_key_and_chords(muzland_songs[2000:])

whole_dataset = get_json('exported-chords.json')
print(len(whole_dataset))
whole_dataset = dataset_to_key_and_chords(whole_dataset)
print(len(whole_dataset))

tf = TonalityFinder(songs_array=train, test_array=test)
print(tf.success_rate(test_chords=test, weights=tf.weights))
revised_weights = tf.find_tonality_multiple_iterations(whole_dataset)
