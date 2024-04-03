import json
import random
from extract_base import extract_chord_base
from find_tonality import get_top_3_score_pairs, find_tonality
from unknown_chords_utils import convert_solfege_chord_to_anglo_saxon
import traceback


def get_random_elements_from_json(file_path):
    with open(file_path, 'r') as file:
        json_array = json.load(file)

        if len(json_array) < 100:
            raise ValueError("The JSON array has fewer than 100 elements.")

        random_elements = random.sample(json_array, 100)
        return random_elements


file_path = 'exported-chords.json'

unknown_chords = ['N.С.', 'N.C.', '¤', 'R', ']A5', 'S', 'H', '%', '2', '`', '`_´', '*', '(', 'h', '\x1aC', 'L', '(',
                  '`', 'N', 'С', '57', 'INTERMEDIO', '022000', '[Am Bbm]', 'С#', 'M', 'Intro', '[D# E]', 'hm', 'ho',
                  '(no3)', 'N.C', '*E', '(A)', '(C)', '\\Am', 'В', 'Вm', 'Pre-coro', '(D', '*Am', '[Bb5/F C5/G]',
                  "'Amaj7", 'M', 'Ñ\x84', ',Dadd9', '9', 'nc', '(G)', 'hammer', 'Аb', '(A)', '?', '(Fsus4)', 'F\u202d#',
                  'А#', '(Fsus4)', ',Eb', '*Asus2', '[F#7 G7]', 'JESÚS', '12']  # 🙏
random_100_elements = get_random_elements_from_json(file_path)

for song_data in random_100_elements:
    try:
        chords_array = song_data[3].split()
        if any(element in chords_array for element in unknown_chords):
            continue

        result = [extract_chord_base(convert_solfege_chord_to_anglo_saxon(chord)) for chord in chords_array]
        print(f"initial song: {song_data}\n")
        find_tonality_top = find_tonality(result)
        for index, pair in enumerate(get_top_3_score_pairs(result)):
            print(
                f"{index + 1}. tonal: {find_tonality_top[index]}, score: {pair[1]}, semitones up: {pair[0][1]}, chords: {pair[0][0]}")
        print('\n\n\n')
    except Exception as e:
        traceback.print_exc()
        print('Unknown chord')
        print(e)
        chords_array = song_data[3].split()
        result = [extract_chord_base(convert_solfege_chord_to_anglo_saxon(chord)) for chord in chords_array]
        print(result)
        print(f"initial song: {song_data}\n")
