import json
import time
from collections import defaultdict

from extract_genre_musicbranz import fetch_artist_genre
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import umap

from t_find_tonality import get_json

file_path = 'MostFrequentChords.json'


def get_artist_to_genre(data):
    artist_to_genre = dict()
    step = 0
    for artist in data:
        artist_to_genre[artist] = fetch_artist_genre(artist_name=artist)
        print(artist, artist_to_genre[artist])
        time.sleep(2)

    with open("artist-to-genre.json", 'w', encoding='utf-8') as file:
        json.dump(artist_to_genre, file)

    return artist_to_genre


def convert_back(data):
    converted_data = {}
    for artist in data:
        converted_data[artist] = {}
        for quality in data[artist]:
            converted_data[artist][quality] = {}
            for length in data[artist][quality]:
                chord_data = data[artist][quality][length]
                new_chord_data = {}
                for chords_str, count in chord_data.items():
                    chords_tuple = tuple(json.loads(chords_str))
                    new_chord_data[chords_tuple] = count
                converted_data[artist][quality][length] = new_chord_data
    return converted_data


def get_most_similar_artists(cosine_sim_df, top_n=5):
    most_similar = {}
    for artist in cosine_sim_df.index:
        similar_artists = cosine_sim_df[artist].sort_values(ascending=False)
        similar_artists = similar_artists.drop(artist)
        most_similar[artist] = similar_artists.head(top_n).index.tolist()
    return most_similar


def build_cosine_comparison(converted_data, quality, length):
    all_chords = set()
    data_for_df = []
    for artist, artist_data in converted_data.items():
        qualities = [quality] if quality in artist_data else []
        if quality == 'all':
            qualities = ['minor', 'major']
        row = {'Artist': artist}
        found_chords = False

        for qual in qualities:
            if qual in artist_data:
                quality_data = artist_data[qual]
                for length_key in [f"{length}"]:
                    if length_key in quality_data:
                        length_data = quality_data[length_key]
                        all_chords.update(length_data.keys())
                        for chord, frequency in length_data.items():
                            row[chord] = row.get(chord, 0) + round(frequency, 1)
                            found_chords = True

        if found_chords:
            data_for_df.append(row)

    if not all_chords:
        raise ValueError("No minor chords found in the dataset.")

    df = pd.DataFrame(data_for_df).fillna(0).set_index('Artist')
    df = df.reindex(columns=all_chords, fill_value=0)

    if df.empty or df.shape[1] == 0:
        raise ValueError("No features (chords) available for similarity computation.")

    cosine_sim_matrix = cosine_similarity(df)
    cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=df.index, columns=df.index)

    return df, cosine_sim_df


def select_top_two_genres(artist_to_genre, stat):
    artist_top_genres = {}

    for artist, genres in artist_to_genre.items():
        top_genres = []
        for genre in genres:
            if genre in stat:
                top_genres.append((genre, stat[genre]))
        top_genres.sort(key=lambda x: x[1], reverse=True)
        artist_top_genres[artist] = top_genres[:1]
    return artist_top_genres


def genre_count(artist_to_genre):
    genre_one_dict = {}
    stat = dict()
    for artist in artist_to_genre:
        if len(artist_to_genre[artist]) == 0:
            continue
        for genre in artist_to_genre[artist]:
            if genre == 'singer-songwriter':
                continue
            if genre in stat:
                stat[genre] += 1
            else:
                stat[genre] = 1

    best_genres = {}
    genre_best_counter = select_top_two_genres(artist_to_genre, stat)
    artist_to_best_genre = {}
    for artist, genres in artist_to_genre.items():
        best_genre = genre_best_counter[artist]
        for b_g in best_genre:
            artist_to_best_genre[artist] = b_g[0]
            genre_one_dict[artist] = {"best_genre": b_g[0]}
            genre_one_dict[artist]["all_genres"] = artist_to_genre[artist]
            if b_g[0] in best_genres:
                best_genres[b_g[0]] += 1
            else:
                best_genres[b_g[0]] = 1
    print(sorted(stat.items(), key=lambda x: x[1], reverse=True))
    return genre_one_dict


def find_key_differences(df, artist1, artist2, threshold=0.1):
    if artist1 not in df.index or artist2 not in df.index:
        raise ValueError("One or both artists not found in the DataFrame.")

    diff = df.loc[artist1] - df.loc[artist2]

    diff_df = pd.DataFrame({
        f'{artist1} - {artist2}': diff,
        f'{artist2} - {artist1}': -diff
    })

    diff_df['Abs Difference'] = diff_df.abs().max(axis=1)
    significant_differences = diff_df[diff_df['Abs Difference'] > threshold]
    key_differences = significant_differences.sort_values('Abs Difference', ascending=False).drop('Abs Difference',
                                                                                axis=1)
    print(key_differences)
    return key_differences


def build_dendrogram(df):
    distance_matrix = pdist(df.values, metric='cosine')
    linked = linkage(distance_matrix, 'complete')
    plt.figure(figsize=(40, 28))
    dendrogram(linked,
               orientation='right',
               labels=df.index.array,
               distance_sort='descending',
               show_leaf_counts=True,
               leaf_font_size=16)
    plt.show()

    n = df.shape[0]
    cluster_map = {i: [df.index[i]] for i in range(n)}
    cluster_history = []

    for i, (cluster1, cluster2, dist, new_cluster_size) in enumerate(linked):
        new_cluster_id = n + i
        merged_items = cluster_map[int(cluster1)] + cluster_map[int(cluster2)]
        cluster_history.append({
            "stage": i + 1,
            "merge": (cluster_map[int(cluster1)], cluster_map[int(cluster2)]),
            "new_cluster_id": new_cluster_id,
            "merged_items": merged_items,
            "distance": dist
        })
        cluster_map[new_cluster_id] = merged_items

    for history in cluster_history:
        print(history)

    with open('cluster_history.json', 'w') as f:
        json.dump(cluster_history, f, indent=4)


with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

artist_to_genre = get_json('artist-to-genre.json')
converted_data = convert_back(data)
artist_to_genre = genre_count(artist_to_genre)
with open('artist-to-best-genres.json', 'w') as f:
    json.dump(artist_to_genre, f, indent=4)

dict_to_dump = defaultdict(lambda: defaultdict(lambda: defaultdict()))
for quality in ['major', 'minor', 'all']:
    print(quality)
    for length in range(1, 5):
        df, cosine_sim_df = build_cosine_comparison(converted_data, quality=quality, length=length)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        most_similar_artists = get_most_similar_artists(cosine_sim_df)

        for artist, similars in most_similar_artists.items():
            find_key_differences(df, artist1="John Prine", artist2="Genesis")
            print(f"Top {len(similars)} similar artists to {artist} are: {similars}")

        # build_dendrogram(df=df)

        distance_matrix = 1 - cosine_sim_df.values
        distance_matrix[distance_matrix < 0] = 0
        try:
            perplexities = [30]
            for perplexity in perplexities:
                tsne = TSNE(n_components=2, perplexity=perplexity, metric="precomputed", init='random')
                embedding = tsne.fit_transform(distance_matrix)
                try:
                    plt.figure(figsize=(12, 12))
                    artists = df.index.tolist()
                    for i, artist in enumerate(artists):
                        x, y = embedding[i]
                        plt.scatter(x, y, color='blue')
                        # plt.annotate(artist, (x, y), textcoords="offset points", xytext=(0, 10), ha='center')
                    plt.title('2D Embedding of Artists Based on Cosine Similarity')
                    plt.xlabel('Dimension 1')
                    plt.ylabel('Dimension 2')
                    plt.grid(True)
                    # plt.show()
                except Exception as e:
                    print(f"Error during plotting: {e}")
        except Exception as e:
            print(f"Error during t-SNE computation: {e}")

        artists_data = [{'artist': artists[i], 'x': float(embedding[i, 0]), 'y': float(embedding[i, 1])} for i in
                        range(len(artists))]

        json_data = json.dumps(artists_data)
        print(json_data)

        dict_to_dump['t-SNE'][quality][length] = artists_data

        reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, random_state=42, metric='cosine', spread=1.0,
                            learning_rate=1.0)
        embedding = reducer.fit_transform(distance_matrix)
        plt.figure(figsize=(12, 10))
        scatter = plt.scatter(embedding[:, 0], embedding[:, 1], alpha=0.5)

        for i, artist in enumerate(artists):
            plt.annotate(artist, (embedding[i, 0], embedding[i, 1]), textcoords="offset points", xytext=(0, 10),
                         ha='center')

        plt.title('UMAP Projection of Artists', fontsize=15)
        plt.xlabel('UMAP Dimension 1')
        plt.ylabel('UMAP Dimension 2')
        plt.grid(True)
        # plt.show()

        artists_data = [{'artist': artists[i], 'x': float(embedding[i, 0]), 'y': float(embedding[i, 1])} for i in
                        range(len(artists))]
        json_data = json.dumps(artists_data)

        dict_to_dump['UMAP'][quality][length] = artists_data

with open('tsne_results.json', 'w') as f:
    json.dump(dict_to_dump, f)
