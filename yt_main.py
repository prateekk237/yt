import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to fetch videos
def search_videos(query):
    search_url = f"https://inv.nadeko.net/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        st.error("Failed to fetch data. Try again later.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    videos = soup.find_all("div", class_="video-card-row")

    if not videos:
        st.warning("No videos found!")
        return []

    results = []
    for video in videos:  # Limit to 10 videos to prevent overload
        title_tag = video.find("a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        video_id = title_tag["href"].split("v=")[-1]
        embed_url = f"https://inv4.nadeko.net/embed/{video_id}"

        results.append({"title": title, "embed_url": embed_url})

    return results

# Use session state to store results
if "search_results" not in st.session_state:
    st.session_state.search_results = []

st.title("🎵 Free YT Music Player")
query = st.text_input("Search for a song or artist")

if st.button("Search"):
    if query:
        st.session_state.search_results = search_videos(query)

# Show search results with play buttons
if st.session_state.search_results:
    for i, video in enumerate(st.session_state.search_results):
        with st.expander(video["title"]):  # Collapsible section for each video
            if st.button(f"▶ Play {i+1}", key=i):
                st.markdown(
                    f'<iframe src="{video["embed_url"]}" width="700" height="400" frameborder="0" allowfullscreen></iframe>',
                    unsafe_allow_html=True,
                )
