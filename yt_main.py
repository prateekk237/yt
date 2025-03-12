import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os

@st.cache_data
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
    for video in videos:
        title_tag = video.find("a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        href = title_tag["href"]

        if "watch?v=" in href:
            video_id = href.split("watch?v=")[-1]
        else:
            continue  # Skip invalid links

        embed_url = f"https://inv4.nadeko.net/embed/{video_id}"
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        results.append({"title": title, "embed_url": embed_url, "thumbnail": thumbnail_url, "video_id": video_id})

    return results

# UI Styling
music_background = """
<style>
    body {
        background-image: url('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4'); 
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp {
        background: rgba(0, 0, 0, 0.7);
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: white;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 10px;
    }
    /* Updated Recent Search Styles */
    .recent-tag button {
        background: #00aaff !important;  /* Sky blue */
        color: black !important;         /* Black text */
        padding: 4px 8px;                /* Smaller size */
        font-size: 14px;                 /* Smaller font */
        border-radius: 12px;             /* Rounded corners */
        margin: 4px;                     /* Space between tags */
        cursor: pointer;                 /* Clickable cursor */
    }
</style>
"""
st.markdown(music_background, unsafe_allow_html=True)

# Streamlit UI
st.title("🎵 Free YT Music Player")
st.write("Designed By: Prateek Malhotra ❤️")

# Initialize session states
if "videos" not in st.session_state:
    st.session_state.videos = []
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []  # Store recent searches

# Search input
query = st.text_input("Search for a song or artist")

# File to store recent searches
RECENT_SEARCHES_FILE = "recent_searches.json"

# Load recent searches from file
def load_recent_searches():
    if os.path.exists(RECENT_SEARCHES_FILE):
        with open(RECENT_SEARCHES_FILE, "r") as f:
            return json.load(f)
    return []

# Save recent searches to file
def save_recent_searches(searches):
    with open(RECENT_SEARCHES_FILE, "w") as f:
        json.dump(searches, f)

# Initialize recent searches
recent_searches = load_recent_searches()

# Add query to recent searches if not already present (limit to 10)
if query and query not in recent_searches:
    recent_searches.insert(0, query)
    recent_searches = recent_searches[:10]
    save_recent_searches(recent_searches)

# Handle removal of a recent search
for recent in recent_searches:
    col1, col2 = st.columns([6, 1])
    with col1:
        if st.button(recent, key=f"recent_{recent}"):
            query = recent
            st.session_state.videos = search_videos(query)
            st.session_state.selected_video = None
            st.rerun()
    with col2:
        if st.button("❌", key=f"remove_{recent}"):
            recent_searches.remove(recent)
            save_recent_searches(recent_searches)
            st.rerun()

# Custom styling for recent search tags
recent_tag_style = """
    <style>
    .recent-tag {
        display: inline-block;
        margin: 5px;
        padding: 5px 10px;
        background: #00aaff; /* Sky blue background */
        color: black;         /* Black text */
        font-size: 14px;      /* Smaller font */
        border-radius: 12px;  /* Rounded corners */
        cursor: pointer;      /* Make it clickable */
    }
    </style>
"""
st.markdown(recent_tag_style, unsafe_allow_html=True)

# Display recent searches section
if recent_searches:
    st.subheader("🔍 Recent Searches")


# Handle search
if st.button("Search"):
    if query:
        st.session_state.videos = search_videos(query)
        st.session_state.selected_video = None  # Reset selected video on new search

        # Store in recent searches (limit to 5)
        if query not in st.session_state.recent_searches:
            st.session_state.recent_searches.insert(0, query)
            if len(st.session_state.recent_searches) > 5:  # Keep last 5 searches
                st.session_state.recent_searches.pop()

# Display videos
for index, video in enumerate(st.session_state.videos):
    st.subheader(video["title"])

    # Show embedded video if selected, else show thumbnail
    if st.session_state.selected_video == video["video_id"]:
        st.markdown(
            f'<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: black;">'
            f'<iframe src="{video["embed_url"]}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" frameborder="0" allowfullscreen></iframe>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Show clickable thumbnail
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(video["thumbnail"], width=150)
        with col2:
            if st.button(f"▶️ Play {video['title']}", key=f"play_{index}"):
                st.session_state.selected_video = video["video_id"]
                st.rerun()  # Rerun app to update UI with selected video
