import requests
from urllib.parse import quote


def fetch_artist_genre(artist_name):
    artist_name_encoded = quote(artist_name)
    url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{artist_name_encoded}&fmt=json&inc=tags"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['artists']:
            artist_data = data['artists'][0]
            genres = [tag['name'] for tag in artist_data.get('tags', []) if tag['count'] > 0]
            return genres
        else:
            return "No artist found."
    except requests.RequestException as e:
        return f"An error occurred: {e}"
