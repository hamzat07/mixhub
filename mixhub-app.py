import streamlit as st
from googleapiclient.discovery import build
import requests
import re


# ===== CONFIG =====
st.set_page_config(page_title="MixHub", page_icon="🎵", layout="wide")

# API Keys - Move to Streamlit Secrets for deployment
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    YOUTUBE_API_KEY = ""  # Leave empty, will be set in Streamlit Cloud

try:
    SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
    SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
except:
    SPOTIFY_CLIENT_ID = ""  # Leave empty, will be set in Streamlit Cloud
    SPOTIFY_CLIENT_SECRET = ""

# ===== FUNCTIONS =====
@st.cache_data(ttl=3600)
def get_spotify_token():
    """Get Spotify access token"""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    
    try:
        auth_url = "https://accounts.spotify.com/api/token"
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        })
        auth_response.raise_for_status()
        return auth_response.json()['access_token']
    except Exception as e:
        st.error(f"Spotify authentication error: {str(e)}")
        return None

def extract_spotify_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    patterns = [
        r'playlist/([a-zA-Z0-9]+)',
        r'spotify:playlist:([a-zA-Z0-9]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_song_artwork_from_spotify(song_name):
    """Get album artwork from Spotify"""
    token = get_spotify_token()
    if not token:
        return None
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        search_response = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params={'q': song_name, 'type': 'track', 'limit': 1}
        )
        search_response.raise_for_status()
        results = search_response.json()
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            if track['album']['images']:
                return track['album']['images'][0]['url']
    except:
        pass
    return None

def import_spotify_playlist(playlist_url):
    """Import playlist from Spotify"""
    playlist_id = extract_spotify_playlist_id(playlist_url)
    if not playlist_id:
        st.error("Invalid Spotify playlist URL")
        return []
    
    token = get_spotify_token()
    if not token:
        st.error("⚠️ Spotify API credentials not configured.")
        return []
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        playlist_response = requests.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers=headers
        )
        playlist_response.raise_for_status()
        playlist_data = playlist_response.json()
        
        songs = []
        for item in playlist_data['tracks']['items']:
            if item['track']:
                track = item['track']
                artist = track['artists'][0]['name'] if track['artists'] else ''
                song_name = f"{track['name']} - {artist}"
                artwork = track['album']['images'][0]['url'] if track['album']['images'] else None
                songs.append({'name': song_name, 'artwork': artwork})
        
        next_url = playlist_data['tracks']['next']
        while next_url:
            response = requests.get(next_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            for item in data['items']:
                if item['track']:
                    track = item['track']
                    artist = track['artists'][0]['name'] if track['artists'] else ''
                    song_name = f"{track['name']} - {artist}"
                    artwork = track['album']['images'][0]['url'] if track['album']['images'] else None
                    songs.append({'name': song_name, 'artwork': artwork})
            next_url = data['next']
        
        return songs
    except Exception as e:
        st.error(f"Error importing Spotify playlist: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def search_youtube_audio(song_name):
    """Search for audio on YouTube and return details"""
    if not YOUTUBE_API_KEY:
        st.error("⚠️ YouTube API key not configured.")
        return None
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=f"{song_name} audio",
            type="video"
        )
        response = request.execute()
        if response["items"]:
            video = response["items"][0]
            video_id = video["id"]["videoId"]
            return {
                "id": video_id,
                "title": video["snippet"]["title"],
                "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                "audio_url": f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        st.error(f"Error searching for '{song_name}': {str(e)}")
    return None

def load_playlist(songs_input):
    """Parse and validate song list"""
    songs = []
    for s in songs_input.split("\n"):
        if s.strip():
            song_name = s.strip()
            # Try to fetch artwork for manually entered songs
            artwork = get_song_artwork_from_spotify(song_name)
            songs.append({'name': song_name, 'artwork': artwork})
    return songs

# ===== CUSTOM CSS =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 50%, #191414 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(29, 185, 84, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    
    .player-container {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border-radius: 25px;
        padding: 2.5rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.4);
        border: 1px solid rgba(29, 185, 84, 0.2);
    }
    
    .album-art-container {
        position: relative;
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }
    
    .album-art {
        border-radius: 20px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.6);
        width: 100%;
        transition: transform 0.3s ease;
    }
    
    .album-art:hover {
        transform: scale(1.02);
    }
    
    .song-title {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin: 1.5rem 0;
        color: #1DB954;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .song-card {
        padding: 1.2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 5px solid #1DB954;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .song-card:hover {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8eaed 100%);
        transform: translateX(10px);
        box-shadow: 0 6px 20px rgba(29, 185, 84, 0.2);
    }
    
    .current-song-card {
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
        color: white;
        font-weight: 600;
        box-shadow: 0 6px 25px rgba(29, 185, 84, 0.4);
    }
    
    .import-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1.8rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .audio-player {
        width: 100%;
        margin: 1rem 0;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .track-info {
        background: rgba(29, 185, 84, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1DB954;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .thumbnail-small {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ===== UI =====
st.markdown('''
    <div class="main-header">
        <h1>🎧 MixHub</h1>
        <p>Your Personal Audio Streaming Experience • Spotify Integration • Beautiful Album Art</p>
    </div>
''', unsafe_allow_html=True)

# Sidebar for playlist management
with st.sidebar:
    st.header("📝 Playlist Manager")
    
    import_method = st.radio(
        "Choose import method:",
        ["🎵 Manual Entry", "🟢 Spotify Playlist"],
        label_visibility="visible"
    )
    
    if import_method == "🟢 Spotify Playlist":
        st.markdown('<div class="import-section">', unsafe_allow_html=True)
        st.write("**Import from Spotify**")
        spotify_url = st.text_input(
            "Paste Spotify Playlist URL:",
            placeholder="https://open.spotify.com/playlist/..."
        )
        
        if st.button("📥 Import from Spotify", type="primary", use_container_width=True):
            if spotify_url:
                with st.spinner("🎵 Importing Spotify playlist..."):
                    imported_songs = import_spotify_playlist(spotify_url)
                    if imported_songs:
                        st.session_state.songs = imported_songs
                        st.session_state.index = 0
                        st.session_state.video_cache = {}
                        st.success(f"✅ Imported {len(imported_songs)} songs!")
                        st.balloons()
                        st.rerun()
            else:
                st.warning("Please enter a Spotify playlist URL")
        
        st.info("💡 **How to get Spotify URL:**\n1. Open Spotify\n2. Right-click playlist\n3. Share → Copy link")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="import-section">', unsafe_allow_html=True)
        songs_input = st.text_area(
            "Enter song names (one per line):",
            height=250,
            placeholder="Example:\nBohemian Rhapsody - Queen\nHotel California - Eagles\nImagine - John Lennon",
            help="Artwork will be automatically fetched from Spotify if available"
        )
        
        if st.button("🔄 Load Playlist", type="primary", use_container_width=True):
            if songs_input:
                with st.spinner("🎨 Loading songs and fetching artwork..."):
                    st.session_state.songs = load_playlist(songs_input)
                    st.session_state.index = 0
                    st.session_state.video_cache = {}
                    st.success(f"✅ Loaded {len(st.session_state.songs)} songs!")
                    st.balloons()
            else:
                st.warning("Please enter some songs first!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if "songs" in st.session_state and st.session_state.songs:
        st.write(f"**📊 Current Playlist:** {len(st.session_state.songs)} songs")
        
        if st.button("💾 Export Playlist", use_container_width=True):
            playlist_text = "\n".join([song['name'] for song in st.session_state.songs])
            st.download_button(
                "⬇️ Download as Text",
                playlist_text,
                "mixhub_playlist.txt",
                use_container_width=True
            )
        
        if st.button("🗑️ Clear Playlist", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# Initialize session state
if "songs" not in st.session_state:
    st.session_state.songs = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "video_cache" not in st.session_state:
    st.session_state.video_cache = {}

# Main content
if st.session_state.songs:
    songs = st.session_state.songs
    current_idx = st.session_state.index
    
    # Player controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⏮️ Previous", use_container_width=True, disabled=(current_idx == 0)):
            st.session_state.index = max(0, current_idx - 1)
            st.rerun()
    
    with col2:
        st.write("")
    
    with col3:
        if st.button("⏭️ Next", use_container_width=True, disabled=(current_idx >= len(songs) - 1)):
            st.session_state.index = min(len(songs) - 1, current_idx + 1)
            st.rerun()
    
    # Current song display
    current_song = songs[current_idx]
    song_name = current_song['name']
    
    if song_name not in st.session_state.video_cache:
        with st.spinner(f"🔍 Finding '{song_name}'..."):
            video_info = search_youtube_audio(song_name)
            if video_info:
                st.session_state.video_cache[song_name] = video_info
    
    if song_name in st.session_state.video_cache:
        video_info = st.session_state.video_cache[song_name]
        
        st.markdown('<div class="player-container">', unsafe_allow_html=True)
        
        col_art, col_player = st.columns([1, 1])
        
        with col_art:
            artwork_url = current_song.get('artwork') or video_info['thumbnail']
            st.markdown('<div class="album-art-container">', unsafe_allow_html=True)
            if artwork_url:
                st.markdown(f'<img src="{artwork_url}" class="album-art">', unsafe_allow_html=True)
            else:
                st.image("https://via.placeholder.com/400x400/1DB954/ffffff?text=♪", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_player:
            st.markdown(f'<div class="song-title">🎵 {song_name}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="track-info">📀 Track {current_idx + 1} of {len(songs)}</div>', unsafe_allow_html=True)
            
            progress = (current_idx + 1) / len(songs)
            st.progress(progress, text=f"Playlist Progress: {current_idx + 1}/{len(songs)}")
            
            st.markdown("---")
            
            video_id = video_info['id']
            st.markdown(f"""
                <iframe 
                    width="100%" 
                    height="100" 
                    src="https://www.youtube.com/embed/{video_id}?autoplay=0&controls=1&modestbranding=1" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen
                    style="border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                </iframe>
            """, unsafe_allow_html=True)
            
            st.info("🎧 **Tip:** Click play to start audio playback")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error(f"❌ Could not find '{song_name}'. Try the next song.")
    
    st.markdown("---")
    
    # Playlist view
    st.subheader("📋 Your Playlist")
    
    for idx, song in enumerate(songs):
        song_name = song['name']
        cols = st.columns([0.3, 0.5, 2.5, 0.7])
        
        with cols[0]:
            if idx == current_idx:
                st.write("🔊")
            else:
                st.write(f"**{idx + 1}**")
        
        with cols[1]:
            if song.get('artwork'):
                st.image(song['artwork'], width=60, use_container_width=False)
            else:
                st.write("🎵")
        
        with cols[2]:
            if idx == current_idx:
                st.markdown(f'<div class="song-card current-song-card">▶ {song_name} (Now Playing)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="song-card">{song_name}</div>', unsafe_allow_html=True)
        
        with cols[3]:
            if idx != current_idx:
                if st.button("▶️ Play", key=f"play_{idx}", use_container_width=True):
                    st.session_state.index = idx
                    st.rerun()

else:
    # Welcome screen
    st.info("👈 **Get Started:** Choose an import method in the sidebar!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎵 Features")
        st.write("✅ Audio-only playback")
        st.write("✅ Beautiful album artwork")
        st.write("✅ Spotify integration")
        st.write("✅ Export playlists")
        st.write("✅ YouTube search")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Quick Start")
        st.write("1️⃣ Choose import method")
        st.write("2️⃣ Add your songs")
        st.write("3️⃣ Click play button")
        st.write("4️⃣ Enjoy music! 🎧")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configuration")
        st.write("**Required API Keys:**")
        st.write("• YouTube Data API v3")
        st.write("• Spotify Client ID")
        st.write("• Spotify Client Secret")
        st.write("")
        st.write("🔗 Set in Streamlit Secrets")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray; padding: 1.5rem; font-size: 0.9rem;">🎵 MixHub • Made with ❤️ using Streamlit • Powered by YouTube & Spotify APIs</div>',
    unsafe_allow_html=True
)
