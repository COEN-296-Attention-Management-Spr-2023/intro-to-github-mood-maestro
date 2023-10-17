import asyncio
from datetime import datetime
import urllib.parse

import aiohttp
from aiolimiter import AsyncLimiter
from quart import Quart, redirect, request, jsonify, session, render_template, url_for

from config import cfg


app = Quart(__name__)
app.secret_key = cfg.secret_key
limiter = AsyncLimiter(cfg.spotify.rate_limit_tokens, cfg.spotify.rate_limit_period)


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


@app.route("/")
async def index():
    return "Welcome to Music Maestro <a href='/login'>Login with Spotify </a>"


@app.route("/login")
async def login():
    params = {
        "client_id": cfg.spotify.id,
        "response_type": "code",
        "scope": "user-read-private user-read-email user-library-read",
        "redirect_uri": f"{request.url_root}callback",
        "show_dialog": True,
    }
    print(f"{request.url_root}callback")

    return redirect(f"{AUTH_URL}?{urllib.parse.urlencode(params)}")


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
            async with cs.post(TOKEN_URL, data=body) as response:
                data = await response.json()

                session["access_token"] = data["access_token"]
                session["refresh_token"] = data["refresh_token"]
                session["expires_at"] = datetime.now().timestamp() + data["expires_in"]

        return redirect("/playlists")


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

        return redirect("/playlists")


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

        for song in songs:
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

            song["artist_genres"] = artist_genres

        return await render_template("liked_songs.html", liked_songs=songs)


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
