from dotenv import load_dotenv
import os
from groq import Groq
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from pydub import AudioSegment

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

transcript_count = 1
audio_count = 1

# Search for content and return the content retrieved.
def search(term,  media=None, country=None, limit=None):
    base_url = f"https://itunes.apple.com/search?term={term}"
    
    if country:
        base_url += f"&country={country}"
    if media:
        base_url += f"&media={media}"
    if limit:
        base_url += f"&limit={limit}"

    # API interaction: Perform GET request to retrieve content
    response = requests.get(base_url)
    
    if response.status_code == 200:
        print("---Successful Request---")
        data = response.json()
        result_count = data.get('resultCount', 0)

        if result_count >= 1:
            print(f"---Found {result_count} {media or 'results'}(s) with specified query:[{term}]---")
            return data['results']
        else:
            print("---Did not find any results with specified term---")
            return []
    else:
        print("---Unsuccessful Request---")
        return []
    
# Filter podcast search results based on a filter term and optional affiliation.
def filter_pod_search_results(podcasts, filter, affiliation=None):
    verified_podcast_episodes = []   
    # Convert names to lowercase for case-insensitive comparison
    filter = filter.lower()
    affiliation = affiliation.lower() if affiliation else None

    # Iterate through each podcast 
    for podcast in podcasts:   
        track_id = podcast.get('trackId')
        artistName = podcast.get('artistName','').lower()
        collectionName = podcast.get('collectionName','').lower()
        # Retrieve episodes from the given podcast
        url = f"https://itunes.apple.com/lookup?id={track_id}&media=podcast&entity=podcastEpisode"
        data = requests.get(url).json()
        print(f"---Found {data['resultCount']} episodes results from a given podcast:[{podcast.get('trackName', '')}]---")
        episodes = data['results'] 
        # Iterate through each episode from the list of episodes
        for episode in episodes:
            trackName = episode.get('trackName', '').lower()
            description = episode.get('description', '').lower()
            
            # Check if the filter appears in the episode name and description of one of the episodes
            name_in_track = filter in trackName
            name_in_description = filter in description
            is_featured = name_in_track and name_in_description

            # Check for affiliation, if provided, in the track, description, collection, or artist name of one of the podcasts episodes
            affiliation_in_track = affiliation in trackName if affiliation else True
            affiliation_in_description = affiliation in description if affiliation else True
            affilation_in_artist = affiliation in artistName if affiliation else True
            affiliation_in_collection = affiliation in collectionName if affiliation else True
            is_affiliated = affiliation_in_description or affiliation_in_track or affilation_in_artist or affiliation_in_collection

            # If the person is featured, and (if provided) affiliation matches, it's a verified podcast episode
            if is_featured and is_affiliated:
                verified_podcast_episodes.append(episode)

    return verified_podcast_episodes

# Retrieve the most recent media from a list of medias (movie, podcast, music, audiobook podcasts episodes, etc..)   
def find_most_recent_media(medias):
    # Check if medias is empty
    if not medias:
        return None
    
    for media in medias:
        # Sort medias, and then retrieve the media with the most recent release date
        most_recent_media = max(medias, key=lambda x: datetime.strptime(x['releaseDate'], '%Y-%m-%dT%H:%M:%SZ'))
    return most_recent_media

# Retrieve audio url (not direct link) from the feed url, use target title to identify item of interests and get the audio url. 
def get_audio_link(feed_url, target_title):
    # Perform GET request to retrieve feed
    response = requests.get(feed_url)
    if response.status_code == 200:
        xml_data = response.content
        root = ET.fromstring(xml_data)
        
        # Iterate through all of the items from the feed
        for item in root.findall('.//item'):
            title = item.find('title').text
            # Check whether the given item has the same title as the target
            if title and title.lower().strip() == target_title.lower():
                # If so, locate enclosure element, and retrieve the audio url from it. (enclosure element contains the audio url)
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    audio_link = enclosure.get('url')
                    return audio_link
    return None

# Get audio file and transcribe it, return the audio file and transcription file. Note: Can use "distil-whisper-large-v3-en" model when default reaches its limit.
def transcribe_audio(audio_file, rate_in_minutes=5, groq_model = "whisper-large-v3"):
    global audio_count, transcript_count  
    mp3_filename = f"audio_{audio_count}.mp3"
    transcript_filename = f"transcription_{transcript_count}.txt"
    
    # Step 1: Download the MP3 file
    response = requests.get(audio_file)
    if response.status_code == 200:
        with open(mp3_filename, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Error downloading MP3: {response.status_code}")
        return
    print("---Downloaded audio mp3 file locally---")

    # Step 2: Split the audio into smaller segments ( Groq AI has audio limitations in place, therefore we need to split large audio files to be smaller segments)
    audio = AudioSegment.from_mp3(mp3_filename)
    segment_length = rate_in_minutes * 60 * 1000  # 10 minutes in milliseconds
    segments = [audio[i:i + segment_length] for i in range(0, len(audio), segment_length)]
    print("---Transcribing---")

    # Step 3: Transcribe each segment using Groq AI's transcribe feature
    client = Groq()
    full_transcription = []  # List to hold transcriptions
    for idx, segment in enumerate(segments):
        segment_filename = f"segment_{idx + 1}.mp3"
        segment.export(segment_filename, format="mp3")
        with open(segment_filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(segment_filename, file.read()),
                model=groq_model,
                prompt="Specify context or spelling",  # Optional
                response_format="json",  # Optional
                language="en",  # Optional
                temperature=0.0  # Optional
            )
            full_transcription.append(transcription.text)  # Add transcription to the list
        # Remove the segment file after processing
        os.remove(segment_filename)

    # Step 4: Merge all transcriptions into a single text
    merged_transcription = "\n".join(full_transcription)
    print("---Transcription completed---")
    
    # Step 5: Write the merged transcription to a text file
    with open(transcript_filename, "w", encoding="utf-8") as text_file:
        text_file.write(merged_transcription)
    
    audio_file_path = os.path.dirname(__file__) + "/" + mp3_filename
    transcript_file_path = os.path.dirname(__file__) + "/" + transcript_filename
    audio_count += 1
    transcript_count += 1
    return (audio_file_path, transcript_file_path)