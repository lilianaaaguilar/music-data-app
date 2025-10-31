from flask import Flask, render_template, request
from markupsafe import Markup
import json

app = Flask(__name__)

@app.route('/')
def render_about():
    return render_template('about.html')
    
@app.route('/databygenre')
def render_databygenre():
    with open('music.json') as music_data:
        songs = json.load(music_data)
    
    genre = request.args.get('genre')
    options = get_genre_options(songs)
    
    if genre:
        top_artists = get_top_artists(genre, songs)
        return render_template('databygenredisplay.html', 
                             genre=genre,
                             artist1=top_artists[0] if len(top_artists) > 0 else "N/A",
                             artist2=top_artists[1] if len(top_artists) > 1 else "N/A",
                             artist3=top_artists[2] if len(top_artists) > 2 else "N/A",
                             options=options)
    else:
        return render_template('databygenre.html', options=options)
        
@app.route('/tempovsyears')
def render_tempovsyears():
    with open('music.json') as music_data:
        songs = json.load(music_data)
    dataPoints = total_annual_tempos(songs)
    return render_template('tempovsyears.html', dataPoints=dataPoints)


def get_genre_options(songs):
    """Get all genres with frequency >= 1.0"""
    genres = []
    for song in songs:
        if "artist" in song and song["artist"]:
        	if "terms" in song["artist"] and "terms_freq" in song["artist"]:
        		terms = song["artist"]["terms"]
        		freq = song["artist"]["terms_freq"]
        		if terms != 0 and freq >= 1.0:
        			genre_name = terms
        			if genre_name not in genres:
        				genres.append(genre_name)
    options = ""
    for genre in sorted(genres):
        options += Markup(f'<option value="{genre}">{genre}</option>')
    return options
    
def get_familiarity(artist_info):
    """Helper function to get the familiarity score from an artist info"""
    return artist_info[1]

def get_top_artists(genre, songs):
    """Get top 3 artists by familiarity for a given genre"""
    artist_scores = {}
    for song in songs:
        if "artist" in song and song["artist"]:
            art = song["artist"]
            if "terms" in art and "terms_freq" in art and "familiarity" in art:
                if art["terms"] == genre:
                    artist_name = art["name"]
                    familiarity = art["familiarity"]
                    if artist_name not in artist_scores or familiarity > artist_scores[artist_name]:
                        artist_scores[artist_name] = familiarity
    sorted_artists = sorted(artist_scores.items(), key=get_familiarity, reverse=True)
    return [f"{artist}" for artist, score in sorted_artists[:3]]
    
def total_annual_tempos(songs):
    """Returns a list of dictionaries {x: year, y: avg_tempo}"""
    year_tempo = {}
    for song in songs:
        if "song" in song and "year" in song["song"] and "tempo" in song["song"]:
            year = song["song"]["year"]
            tempo = song["song"]["tempo"]
            if year > 0 and tempo > 0:
                if year in year_tempo:
                    year_tempo[year].append(tempo)
                else:
                    year_tempo[year] = [tempo]
    dataPoints = []
    for year in sorted(year_tempo):
        avg_tempo = sum(year_tempo[year]) / len(year_tempo[year])
        dataPoints.append({"x": year, "y": round(avg_tempo, 2)})
    return dataPoints
	
if __name__=="__main__":
    app.run(debug=True)