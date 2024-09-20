import itunes_search

def run_task(speaker, affiliation=None):
    pod_results = itunes_search.search(speaker, "podcast")
    if pod_results is None:
        return
    
    filtered_results = itunes_search.filter_pod_search_results(pod_results, speaker, affiliation)
    if filtered_results:
        print(f"---Found {len(filtered_results)} verified podcast episodes featuring {speaker} with affilation:{affiliation}---")
    else:
        print(f"---No verified podcasts found for {speaker}---")
        return

    most_recent_episode = itunes_search.find_most_recent_media(filtered_results)
    if most_recent_episode:
        print(f"---Most recent podcast episode:[{most_recent_episode['trackName']}]---")
    else:
        print("---Could not find most recent podcast from verified podcast results---")
        return 
    
    audio_link = itunes_search.get_audio_link(most_recent_episode['feedUrl'],most_recent_episode['trackName'])
    file_paths = itunes_search.transcribe_audio(audio_link)
    return (most_recent_episode['trackViewUrl'], file_paths[0], file_paths[1])

if __name__ == "__main__":
    print(run_task("Kevin Durant"))
    print(run_task("Kevin Durant", "Logan Paul"))
