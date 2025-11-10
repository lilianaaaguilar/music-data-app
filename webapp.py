from flask import Flask, render_template, request
from markupsafe import Markup
import json

app = Flask(__name__)

with open('music.json') as f:
    SONGS = json.load(f)

@app.route('/')
def render_about():
    return render_template('about.html')
    
@app.route('/databygenre')
def render_databygenre():
    songs = SONGS
    genre = request.args.get('genre')
    options = get_genre_options(songs)
    
    if genre:
        top_artists = get_top_artists(genre, songs)
        count = get_genre_count(genre, songs)
    
    if genre:
        top_artists = get_top_artists(genre, songs)
        return render_template('databygenredisplay.html', 
                             genre=genre,
                             artist1=top_artists[0] if len(top_artists) > 0 else "N/A",
                             artist2=top_artists[1] if len(top_artists) > 1 else "N/A",
                             artist3=top_artists[2] if len(top_artists) > 2 else "N/A",
                             options=options,
                             count=count)
    else:
        return render_template('databygenre.html', options=options)
        
@app.route('/durationbyyear')
def render_durationbyyear():
    year_options = get_year_options(SONGS)
    year = request.args.get('year')
    if year:
        year = int(year)
        longest, shortest = get_duration_stats_by_year(year, SONGS)
        count = get_song_count_by_year(year, SONGS)
        if longest is not None and shortest is not None:
            return render_template(
                'durationbyyeardisplay.html',
                year_options=year_options,
                year=year,
                longest=longest,
                shortest=shortest,
                count=count)
        else:
            return render_template(
                'durationbyyear.html',
                year_options=year_options,
                message=f"No songs found for {year}.")
    return render_template('durationbyyear.html', year_options=year_options)
        
@app.route('/tempovsyears')
def render_tempovsyears():
    songs = SONGS
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
    sorted_artists = sorted(artist_scores.items(), key=lambda x: x[1], reverse=True)
    return [artist for artist, _ in sorted_artists[:3]]
    
def get_year_options(songs):
    """Get all years for dropdown options"""
    years = []
    for song in songs:
        if "song" in song and "year" in song["song"]:
            year = song["song"]["year"]
            if year != 0 and year not in years:
                years.append(year)
    yearz = ""
    for year in sorted(years):
        yearz += Markup(f'<option value="{year}">{year}</option>')
    return yearz
    
def get_duration_stats_by_year(year, songs):
    """Return longest and shortest song durations for the selected year"""
    songs_in_year = [s for s in songs if s["song"]["year"] == year]
    if not songs_in_year:
        return None, None
    durations = [s["song"]["duration"] for s in songs_in_year if "duration" in s["song"]]
    if not durations:
        return None, None
    longest = round(max(durations), 2)
    shortest = round(min(durations), 2)
    return longest, shortest
    
def get_genre_count(genre, songs):
    """Return the number of songs that belong to the selected genre."""
    genre_songs = [
        s for s in songs
        if "artist" in s and s["artist"]
        and "terms" in s["artist"] and s["artist"]["terms"] == genre]
    return len(genre_songs)
    
def get_song_count_by_year(year, songs):
    """Return the number of songs for the selected year."""
    songs_in_year = [s for s in songs if "song" in s and s["song"].get("year") == year]
    return len(songs_in_year)

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