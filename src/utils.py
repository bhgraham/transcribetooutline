def format_timestamp(timestamp):
    # Convert a timestamp string into a standardized format
    from datetime import datetime
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").isoformat()
    except ValueError:
        raise ValueError("Timestamp must be in 'YYYY-MM-DD HH:MM:SS' format.")

def is_overlapping(start1, end1, start2, end2):
    # Check if two time intervals overlap
    return max(start1, start2) < min(end1, end2)

def remove_duplicates(transcripts):
    # Remove duplicate transcripts based on their content
    seen = set()
    unique_transcripts = []
    for transcript in transcripts:
        if transcript not in seen:
            seen.add(transcript)
            unique_transcripts.append(transcript)
    return unique_transcripts