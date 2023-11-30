import asyncio
from datetime import datetime
import json
import select
import urllib.parse


import aiohttp
from aiolimiter import AsyncLimiter
from quart import Quart, redirect, request, jsonify, session, render_template, url_for

from config import cfg
import db
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert


user_id = ""
app = Quart(__name__)
app.secret_key = cfg.secret_key
limiter = AsyncLimiter(cfg.spotify.rate_limit_tokens, cfg.spotify.rate_limit_period)


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


@app.route("/")
async def index():
    # return "Welcome to Music Maestro <a href='/login'>Login with Spotify </a>"
    # return redirect("/welcome.html")
    return await render_template("welcome.html")


@app.route("/login")
async def login():
    params = {
        "client_id": cfg.spotify.id,
        "response_type": "code",
        "scope": "user-read-private user-read-email user-library-read playlist-modify-public playlist-modify-private",
        "redirect_uri": f"{request.url_root}callback",
        "show_dialog": True,
    }
    print(f"{request.url_root}callback")

    return redirect(f"{AUTH_URL}?{urllib.parse.urlencode(params)}")


@app.route("/home")
async def home():
    return await render_template("home.html")


@app.route("/callback")
async def callback():
    if "error" in request.args:
        return jsonify({"error": request.args["error"]})

    if "code" in request.args:
        body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": f"{request.url_root}callback",
            "client_id": cfg.spotify.id,
            "client_secret": cfg.spotify.secret,
        }

        async with aiohttp.ClientSession() as cs:
            async with (limiter, cs.post(TOKEN_URL, data=body) as response):
                data = await response.json()
                session["access_token"] = data["access_token"]
                session["refresh_token"] = data["refresh_token"]
                session["expires_at"] = datetime.now().timestamp() + data["expires_in"]

            url = f"{API_BASE_URL}me"
            headers = {
                "Authorization": f"Bearer {session['access_token']}"
            }
            async with (
                limiter,
                cs.get(url, headers=headers) as response,
            ):
                data = await response.json()
                session["spotify_id"] = data["id"]

        return redirect("/home")

@app.route("/refresh-token")
async def refresh_token():
    if "refresh token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": cfg.spotify.id,
            "client_secret": cfg.spotify.secret,
        }

        async with aiohttp.ClientSession() as cs:
            async with cs.post(TOKEN_URL, data=body) as response:
                data = await response.json()

                session["access_token"] = data["access_token"]
                session["expires_at"] = datetime.now().timestamp() + data["expires_in"]

        return redirect("/home")

async def update_database_features(songs, headers):
    async with db.async_session() as db_session2:
        for song in songs:
            place = song["track"]["id"]
            result = (await db_session2.execute(select(db.SongData).where(db.SongData.id == place))).first()
            if result[0].features is not None :
                continue
            feature_data = await get_song_features(song["track"]["id"], headers)
            statement = (
                update(db.SongData)
                .where(db.SongData.id == place)
                .values(features=feature_data)
            )
            await db_session2.execute(statement)
            await db_session2.commit()

async def update_database_genres(songs, headers):
    async with db.async_session() as db_session3:
        for song in songs:
            place = song["track"]["id"]
            result = (await db_session3.execute(select(db.SongData).where(db.SongData.id == place))).first()
            if result[0].genres is not None :
                continue
            genre_data = await get_song_genres(song, headers)
            statement = (
                update(db.SongData)
                .where(db.SongData.id == place)
                .values(genres=genre_data)
            )
            await db_session3.execute(statement)
            await db_session3.commit()



async def get_song_features(song_id, headers):
    async with aiohttp.ClientSession() as cs:
        url = f"{API_BASE_URL}audio-features/{song_id}"
        async with (
                limiter,
                cs.get(url, headers=headers) as response,
            ):
                data = await response.json()
        return data
    

async def get_song_genres(song, headers):
    async with aiohttp.ClientSession() as cs:
        track_info = song["track"]
        artists_info = track_info["artists"]
        artist_genres = []
        for artist in artists_info:
            url = f"{API_BASE_URL}artists/{artist['id']}"

            async with (
                limiter,
                cs.get(url, headers=headers) as response,
            ):
                data = await response.json()
                artist_genres.extend(data.get("genres", []))

        return artist_genres


@app.route("/liked_songs")
async def get_liked_songs():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    async with aiohttp.ClientSession() as cs:
        songs = []

        url = f"{API_BASE_URL}me/tracks"
        headers = {
            "Authorization": f"Bearer {session['access_token']}"
        }

        while url:
            async with (
                limiter,
                cs.get(url, headers=headers) as response,
            ):
                data = await response.json()
                songs.extend(data.get("items", []))
                url = data.get("next")
            
        playlist_songs = []
        for song in songs:
            playlist_songs.append(song["track"]["id"])

        async with db.async_session() as db_session:
        
            stmt = sqlite_upsert(db.SongData).values(
                [
                    dict(id=song["track"]["id"], name = song["track"]["name"], artists=song["track"]["artists"])
                    for song in songs
                ]
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[db.SongData.id], set_=dict(artists=stmt.excluded.artists)
            )
            await db_session.execute(stmt)
            await db_session.commit()

        asyncio.create_task(update_database_genres(songs, headers))
        asyncio.create_task(update_database_features(songs, headers))
         
        return await render_template("liked_songs_ajax.html", liked_songs=songs)

@app.route("/get_updated_songs")
async def get_updated_songs():
    async with db.async_session() as session:
        result = await session.execute(select(db.SongData))

        song_data = []
        for row in result.scalars():
            song_dict = {
                'id': row.id,
                'genres': row.genres,
                'features': row.features
            }
            song_data.append(song_dict)

    return jsonify(song_data)

@app.route('/table')
async def table():
    async with db.async_session() as db.session3:
        result = await db.session3.execute(select(db.SongData))
        songs = result.scalars().all()
        data = [{'id': song.id, 'name': song.name, 'artists': ", ".join(a["name"] for a in song.artists), 'genres': song.genres, 'features': song.features} for song in songs]
    return await render_template('table.html', data=data)
 
@app.route('/submit-form', methods=['POST'])
async def handle_form_submission():
    form_data = await request.form
    playlist_name = form_data.get('textInput')
    print("Playlist Name:", playlist_name)
    return redirect(url_for('table'))  

@app.route("/create-playlist2", methods=["POST"])
async def create_playlist2():
    if "access_token" not in session:
        return redirect("/login")
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    data = await request.get_json()
    playlist_name = data.get('name')
    song_ids = data.get('songs')


    url = f"{API_BASE_URL}users/{session['spotify_id']}/playlists"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json"
    }
    body = {
        "name": request.args.get("name", default=playlist_name),
        "description": request.args.get("description", default="Placeholder Description."),
        "public": False,
    }
    async with (limiter, aiohttp.ClientSession() as cs, cs.post(url, headers=headers, json=body) as response):
        data = await response.json()
        playlist_id = data["id"]

    url = f"{API_BASE_URL}playlists/{playlist_id}/tracks"
    body = {
        "uris": [f"spotify:track:{track_id}" for track_id in song_ids],
        "position": 0,
    }

    async with (limiter, aiohttp.ClientSession() as cs, cs.post(url, headers=headers, json=body) as response):
        return jsonify({"message": "Playlist created", "playlist_id": playlist_id})


async def get_playlists_songs(user_token: str, playlist: dict) -> dict:
    async with aiohttp.ClientSession() as cs:
        url = f"{API_BASE_URL}playlists/{playlist['id']}"
        headers = {
            "Authorization": f"Bearer {user_token}"
        }

        async with (
            limiter,
            cs.get(url, headers=headers) as response
        ):
            data = await response.json()
            image = data.get("images")[0]["url"] if "images" in data else ""

        url = f"{API_BASE_URL}playlists/{playlist['id']}/tracks"

        async with(
            limiter,
            cs.get(url, headers=headers) as response
        ):
            data = await response.json()
            tracks = [
                {
                    "name": track["track"]["name"],
                    "artists": [artist["name"] for artist in track["track"]["artists"]],
                }
                for track in data["items"]
            ]

        return {
            "name": playlist["name"],
            "image": image,
            "tracks": tracks,
        }


@app.route("/playlists")
async def get_playlists():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"{API_BASE_URL}me/playlists", headers=headers) as response:
            data = await response.json()
            info = await asyncio.gather(
                *[
                    get_playlists_songs(session["access_token"], playlist)
                    for playlist in data["items"]
                ]
            )

            return await render_template("playlists.html", playlists=info)

