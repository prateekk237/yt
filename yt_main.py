import streamlit as st
import requests
from bs4 import BeautifulSoup


# Function to fetch all videos
def search_videos(query):
    search_url = f"https://inv.nadeko.net/search?q={query.replace(' ', '+')}"
    #headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url
                            #, headers=headers
                           )

    if response.status_code != 200:
        st.error("Failed to fetch data. Try again later.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    videos = soup.find_all("div", class_="video-card-row")
    if not videos:
        st.warning("No videos found!")
        return []

    results = []
    for video in videos:  # No limit, fetch all videos
        title_tag = video.find("a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        video_id = title_tag["href"].split("v=")[-1]  # Extract YouTube video ID
        embed_url = f"https://inv4.nadeko.net/embed/{video_id}"

        results.append({"title": title, "embed_url": embed_url})

    return results

music_background = """
<style>
    body {
        background-image: url('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4'); /* Replace with any music-themed image URL */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp {
        background: rgba(0, 0, 0, 0.7);  /* Dark overlay for better visibility */
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: white;
    }
    .stButton>button {
        background-color: #ff4b4b; /* Red like a music play button */
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 10px;
    }
</style>
"""

# Apply CSS
#st.markdown(music_background, unsafe_allow_html=True)

# Streamlit UI
st.title("🎵 Free YT Music Player")
st.write("Designed By: Prateek Malhotra ❤️")

# Search bar
query = st.text_input("Search for a song or artist")

if st.button("Search"):
    if query:
        st.session_state.search_results = search_videos(query) 

    if videos:
        for video in videos:  # Display all videos
            st.subheader(video["title"])
            st.markdown(
                f'<iframe src="{video["embed_url"]}" width="700" height="400" frameborder="0" allowfullscreen></iframe>',
                unsafe_allow_html=True,
            )
    else:
        st.warning("No videos found!")
