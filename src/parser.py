import re


class TranscriptParser:
    def __init__(self, transcript_text):
        self.transcript_text = transcript_text
        self.transcripts = []

    def parse_transcript(self):
        lines = self.transcript_text.splitlines()
        for line in lines:
            result = self.extract_timestamps(line)
            if result:
                timestamp, class_type, content = result
                self.transcripts.append({
                    'timestamp': timestamp,
                    'class_type': class_type,
                    'content': content
                })

    def extract_timestamps(self, line):
        # Only extract timestamp and content if present, otherwise just return content
        import re
        match = re.match(r"\[(.*?)\]\s*(.*)", line)
        if match:
            timestamp, content = match.groups()
            return timestamp.strip(), "Unknown", content.strip()
        if line.strip():
            return None, "Unknown", line.strip()
        return None, "Unknown", ""

    def separate_classes(self):
        class_dict = {}
        for transcript in self.transcripts:
            class_type = transcript['class_type']
            if class_type not in class_dict:
                class_dict[class_type] = []
            class_dict[class_type].append(transcript)
        return class_dict

    def detect_overlaps(self):
        # Logic to detect overlapping timestamps
        overlaps = []
        timestamps = [transcript['timestamp'] for transcript in self.transcripts]
        for i in range(len(timestamps)):
            for j in range(i + 1, len(timestamps)):
                if self.is_overlapping(timestamps[i], timestamps[j]):
                    overlaps.append((timestamps[i], timestamps[j]))
        return overlaps

    def is_overlapping(self, timestamp1, timestamp2):
        # Placeholder for actual overlap detection logic
        return timestamp1 == timestamp2

    def detect_duplicates(self):
        seen = set()
        duplicates = []
        for transcript in self.transcripts:
            content = transcript['content']
            if content in seen:
                duplicates.append(content)
            else:
                seen.add(content)
        return duplicates