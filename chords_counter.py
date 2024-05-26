def count_chord_frequencies(chords, max_sequence_length):
    frequencies = {i: {} for i in range(1, max_sequence_length + 1)}
    for i in range(len(chords)):
        for length in range(1, max_sequence_length + 1):
            if i + length <= len(chords):
                seq = tuple(chords[i:i + length])
                frequencies[length][seq] = 1

    return frequencies
