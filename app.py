import streamlit as st
import requests
import time
from datetime import datetime
import twitchAuth


@st.cache_data
def _IGDBQuery(game_count:int, min_rating:int):
    url = "https://api.igdb.com/v4/games"
    params = {
        "headers": {
            "Client-ID": st.secrets['CLIENT_ID'],
            "Authorization": f"{auth.token_type} {auth.access_token}",
        },
        "data": f"fields id,name,rating,cover.*,first_release_date,game_engines.*,summary,url; where rating > {min_rating}; limit {game_count};"
    }
    
    resp = requests.post(url, **params)
    if resp.status_code == 200:
        print("IGDB query successful")
        return resp.json()
    else:
        print(f"IGDB query error: {resp.status_code}")
        return None


def Main():
    st.title("IGDB High Rating Games")

    if not auth.authenticated:
        st.warning("Authentication failed")
        return

    with st.sidebar:
        refresh_rate = st.selectbox(label="refresh rate", options=[3, 5, 15, 30])
        game_count = st.slider(label="game count", min_value=3, max_value=30, value=5)
        min_rating = st.slider(label="minimum rating", min_value=1, max_value=99, value=85)

    placeholder = st.empty()

    data = _IGDBQuery(game_count=int(game_count), min_rating=min_rating)
    if data != None:
        i = 0
        while True:
            with placeholder.container():
                st.header(data[i]['name'])

                col3, col4 = st.columns([0.3, 0.7])
                with col3:
                    cover_url = data[i]['cover']['url']
                    cover_url = cover_url.replace("t_thumb", "t_cover_big")
                    if cover_url.startswith("//"):
                        cover_url = f"http:{cover_url}"
                    st.image(cover_url)

                with col4:

                    release_date = datetime.fromtimestamp(int(data[i]['first_release_date'])).strftime('%Y-%m-%d')
                    st.write(f"release date: {release_date}")

                    st.write(f"rating: {data[i]['rating']:.1f}")

                    if 'game_engines' in data[i].keys():
                        engines = [engine['name'] for engine in data[i]['game_engines']]
                        st.write("game engine: " + ", ".join(engines))

                    st.page_link(data[i]['url'], label="IGDB page")

                    st.write(data[i]['summary'])

            i += 1
            if i == len(data):
                i = 0
            time.sleep(refresh_rate)

            placeholder.empty()
            
            # delay required to ensure the placeholder is properly cleared
            time.sleep(0.1)



if __name__ == "__main__":
    auth = twitchAuth.Auth(client_id=st.secrets['CLIENT_ID'], client_secret=st.secrets['CLIENT_SECRET'])
    Main()
