import streamlit as st
import requests
from bs4 import BeautifulSoup


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
</style>
"""
st.markdown(music_background, unsafe_allow_html=True)

# Streamlit UI
st.title("🎵 Free YT Music Player")
st.write("Designed By: Prateek Malhotra ❤️")

query = st.text_input("Search for a song or artist")

# Store video data in session state
if "videos" not in st.session_state:
    st.session_state.videos = []
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None

if st.button("Search"):
    if query:
        st.session_state.videos = search_videos(query)
        st.session_state.selected_video = None  # Reset selected video on new search

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
