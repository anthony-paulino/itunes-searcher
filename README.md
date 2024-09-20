Goal:
Create a web scraper that can search for and transcribe the latest podcast featuring a specified person.

Objective:
Given a specific person’s name and an optional affiliation (e.g., “Keith Rabois from Khosla Ventures”), the scraper should:

1. Search the web to find the most recent podcast the person has appeared on.
2. Verify that the podcast features the correct person by cross-referencing available metadata (e.g., episode title, description, speaker list).
3. Transcribe the podcast using the Groq API for transcription (Llama or another LLM)
4. Return the following:
    • A link to the podcast.
    • The transcription of the podcast.

Setup
1. Install all of the required python libraries, run the following command "pip install -r requirements.txt".
2. Download ffmpeg from https://www.gyan.dev/ffmpeg/builds/#release-builds, (if your on windows "ffmpeg-release-full.7z".) Extract the zip folder and rename the folder to "FFmpeg" and place it in "C:\"
3. Run cmd as administrator, and run "setx /m PATH "C:\ffmpeg\bin;%PATH%".
4. Verify ffmpeg Installation by running the following command "ffmpeg -version".

Note: 
1. Swap between models when you reach rate limit
2. Groq AI's limitation:
    • Max File Size: 25 MB
    • Minimum File Length: .01 seconds
    • Supported File Types: mp3, mp4, mpeg, mpga, m4a, wav, webm
    • Single Audio Track: Only the first track will be transcribed for files with multiple audio tracks. (e.g. dubbed video)
    • Supported Response Formats: json, verbose_json, text

Environmental Variable:
Set your groq api key to an environmental called "GROQ_API_KEY". Can do it through a .env and loading/extracting the way I did.

# Itunes Searcher

> search for content within the iTunes Catalog

`Itunes Searcher` finds content via [iTunes Search API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html).

Search parameters:
-   _term_ - search string (name, author, etc)
-   _media_ - media type (movie,music, podcast, etc)
-   _country_ - ISO alpha-2 country code (us, de, fr, etc)
-   _limit_ - maximum number or search result

## Installation

1. Install all of the required python libraries, run the following command '''sh pip install -r requirements.txt'''
2. Download ffmpeg from https://www.gyan.dev/ffmpeg/builds/#release-builds, (if your on windows "ffmpeg-release-full.7z".) Extract the zip folder and rename the folder to "FFmpeg" and place it in "C:\"
3. Run cmd as administrator, and run "setx /m PATH sh'''C:\ffmpeg\bin;%PATH%"'''
4. Verify ffmpeg Installation by running the following command ''''sh ffmpeg -version'''

## Future Improvements:
- Create an Itunes class with general search and look up methods
- Create a media class (base/parent class) with (sub/child) classes that contain podcast, movie, music, audiobooks, etc where they'll have field members such as id, name, url, feed, media type, image, any other more specific fields for each different media type. 
-  Provide much more general functions and more specific functions tailored for different media types, etc. 