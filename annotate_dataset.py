import json

from find_tonality_with_quality import TonalityWithQualityFinder
from t_find_tonality import add_key_to_songs, major_weights, minor_weights, get_json, dataset_to_key_and_chords

if __name__ == '__main__':
    muzland_songs = get_json('muzland.json')

    train = dataset_to_key_and_chords(muzland_songs[:2000])
    test = dataset_to_key_and_chords(muzland_songs[2000:])

    whole_dataset_json = get_json('exported-chords.json')
    print(len(whole_dataset_json))
    whole_dataset = dataset_to_key_and_chords(whole_dataset_json)

    tonalityWithQualityFinder = TonalityWithQualityFinder(songs_array=train, test_array=test)

    # revised_weights = tonalityWithQualityFinder.find_tonality_multiple_iterations(songs_array=whole_dataset)

    annotated = add_key_to_songs(songs_array=whole_dataset, tonality_with_quality_finder=tonalityWithQualityFinder,
                                 major_weights=major_weights, minor_weights=minor_weights)

    file_path = 'annotated-exported-chords.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(annotated, file)

    # annotated = add_key_to_songs(songs_array=whole_dataset, tonality_with_quality_finder=tonalityWithQualityFinder,
    #                      major_weights=major_weights, minor_weights=minor_weights)
