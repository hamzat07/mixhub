

🎧 MixHub - Audio Streaming Player   https://mixapp-x7psnbdb2uul5wrgjhe4b3.streamlit.app/
A beautiful, modern audio streaming application built with Streamlit that integrates with YouTube and Spotify APIs to provide a seamless music listening experience with album artwork.

✨ Features

🎵 Audio-Only Playback - Stream music from YouTube
🖼️ Beautiful Album Artwork - Automatically fetched from Spotify
🟢 Spotify Integration - Import entire playlists instantly
📝 Manual Playlist Creation - Add songs one by one
💾 Export Playlists - Save your playlists as text files
🎨 Modern UI - Clean, gradient-based design with smooth animations
📱 Responsive Design - Works on desktop and mobile

🚀 Quick Start
Prerequisites
You'll need API credentials for:

YouTube Data API v3 - Get it here
Spotify Client ID & Secret - Get it here

Local Installation

Clone this repository:

bashgit clone https://github.com/hamza07/mixhub.git
cd mixhub

Install dependencies:

bashpip install -r requirements.txt

Create .streamlit/secrets.toml file:

YOUTUBE_API_KEY = "your_youtube_api_key"
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"

Run the app:

bashstreamlit run app.py
🌐 Deploy to Streamlit Cloud

Fork this repository
Go to share.streamlit.io
Connect your GitHub account
Select your forked repository
Add your API keys in Settings → Secrets:

YOUTUBE_API_KEY = "your_youtube_api_key"
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"

Click Deploy!

📖 How to Use
Import from Spotify

Open Spotify and find a playlist
Right-click the playlist → Share → Copy link
Paste the URL in MixHub
Click "Import from Spotify"

Manual Entry

Select "Manual Entry" mode
Type song names (one per line)
Format: Song Name - Artist
Click "Load Playlist"

Playback Controls

▶️ Click any song to play
⏮️ Previous track
⏭️ Next track
💾 Export playlist

🔑 Getting API Keys
YouTube API Key

Go to Google Cloud Console
Create a new project
Enable "YouTube Data API v3"
Create credentials (API Key)
Copy your API key

Spotify API Credentials

Go to Spotify Developer Dashboard
Log in and create an app
Copy your Client ID and Client Secret

🛠️ Tech Stack

Frontend: Streamlit
APIs: YouTube Data API v3, Spotify Web API
Languages: Python 3.8+
Styling: Custom CSS with gradients and animations

📁 Project Structure:
mixhub/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .streamlit/
    └── secrets.toml      # API credentials (not in repo)
