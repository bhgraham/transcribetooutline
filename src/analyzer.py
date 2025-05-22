import os
import openai
import re
from collections import defaultdict
from difflib import SequenceMatcher
from parser import TranscriptParser
import fnmatch


def detect_subject_text(transcript, api_key, max_chars=2000):
    # Only use the first max_chars characters for subject detection
    sample = transcript[:max_chars]
    prompt = (
        "You are an expert at classifying transcripts by subject. "
        "Given the following transcript, return ONLY the most likely subject as a single word or phrase. "
        "Possible subjects are law school courses (e.g., Torts, Contracts, Property, Criminal Law, Constitutional Law, Civil Procedure, Legal Writing, Professional Responsibility, Administrative Law, etc.) "
        "or 'Medical' if the transcript is about medical topics. "
        "If you are unsure, return 'Unknown'.\n\n"
        f"Transcript:\n{sample}\n\nSubject:"
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def outline_with_gpt_text(transcript, api_key, subject):
    prompt = (
        f"You are an expert legal educator. "
        f"Take the following transcript and turn it into a clear, organized outline for the subject '{subject}'. "
        "Use headings and bullet points. Focus on the main topics, subtopics, and key details. "
        "Highlight anything that is repeated, emphasized, or marked as important by the speaker, "
        "especially if they mention tests or exams—add a flag or note for those items. "
        "Do not include extraneous information. Here is the transcript:\n\n"
        f"{transcript}"
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0.3,
    )
    return response.choices[0].message.content


def remove_overlaps_and_duplicates(texts):
    # Remove exact duplicates
    unique_texts = []
    seen = set()
    for t in texts:
        t_clean = t.strip()
        if t_clean not in seen:
            unique_texts.append(t_clean)
            seen.add(t_clean)
    # Remove overlaps (simple: if last 10 lines of one are similar to first 10 of next, trim)
    cleaned = []
    for i, t in enumerate(unique_texts):
        if i == 0:
            cleaned.append(t)
        else:
            prev = cleaned[-1]
            prev_lines = prev.splitlines()
            curr_lines = t.splitlines()
            overlap = False
            for n in range(10, 0, -1):
                if len(prev_lines) >= n and len(curr_lines) >= n:
                    prev_tail = "\n".join(prev_lines[-n:])
                    curr_head = "\n".join(curr_lines[:n])
                    ratio = SequenceMatcher(None, prev_tail, curr_head).ratio()
                    if ratio > 0.7:
                        cleaned[-1] = "\n".join(prev_lines[:-n])
                        cleaned.append(t)
                        overlap = True
                        break
            if not overlap:
                cleaned.append(t)
    return "\n\n".join(cleaned)


def chunk_text(text, max_chars=12000):
    # Split text into chunks of up to max_chars, trying to split at paragraph boundaries
    paragraphs = text.split('\n\n')
    chunks = []
    current = []
    current_len = 0
    for para in paragraphs:
        if current_len + len(para) + 2 > max_chars and current:
            chunks.append('\n\n'.join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para) + 2
    if current:
        chunks.append('\n\n'.join(current))
    return chunks


class TranscriptAnalyzer:
    def __init__(self, transcripts_dir="."):
        self.transcripts_dir = transcripts_dir

    def run(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set your OPENAI_API_KEY environment variable.")

        # Exclude previously generated files
        transcript_files = [
            f for f in os.listdir(self.transcripts_dir)
            if (
                f.endswith(".txt")
                and os.path.isfile(os.path.join(self.transcripts_dir, f))
                and not fnmatch.fnmatch(f, "*-alldata.txt")
                and not fnmatch.fnmatch(f, "*-alldata.txt.*")
                and not fnmatch.fnmatch(f, "*-outline.txt")
                and not fnmatch.fnmatch(f, "*-outline.txt.*")
            )
        ]
        if not transcript_files:
            print("No transcript files found.")
            return

        # Step 1: Categorize files by subject
        subject_files = defaultdict(list)
        for fname in sorted(transcript_files):
            path = os.path.join(self.transcripts_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            subject = detect_subject_text(content, api_key)
            if subject.lower() == "unknown":
                subject = "misc"
            safe_subject = re.sub(r'[^a-zA-Z0-9_]+', '_', subject.strip().lower())
            subject_files[safe_subject].append((fname, content))

        # Step 2: Concatenate files per subject (do not overwrite existing files)
        for subject, files in subject_files.items():
            outdata_name = f"{subject}-alldata.txt"
            outdata_path = os.path.join(self.transcripts_dir, outdata_name)
            if os.path.exists(outdata_path):
                # Don't overwrite, create a new numbered file
                i = 1
                while os.path.exists(os.path.join(self.transcripts_dir, f"{subject}-alldata-{i}.txt")):
                    i += 1
                outdata_path = os.path.join(self.transcripts_dir, f"{subject}-alldata-{i}.txt")

            # Parse and collect all transcript chunks with timestamps
            transcript_chunks = []
            for fname, content in files:
                parser = TranscriptParser(content)
                parser.parse_transcript()
                for entry in parser.transcripts:
                    # Use timestamp if available, else fallback to filename
                    timestamp = entry.get('timestamp') or fname
                    transcript_chunks.append((timestamp, entry['content']))

            # Sort by timestamp (or filename if no timestamp)
            def sort_key(item):
                ts, _ = item
                # Try to parse as datetime, fallback to string
                import datetime
                try:
                    return datetime.datetime.fromisoformat(ts.replace('/', '-').replace('_', ' '))
                except Exception:
                    return ts
            transcript_chunks_sorted = sorted(transcript_chunks, key=sort_key)

            # Get only the content, in order
            texts = [content for _, content in transcript_chunks_sorted]
            cleaned = remove_overlaps_and_duplicates(texts)

            mode = "a" if os.path.exists(outdata_path) else "w"
            with open(outdata_path, mode, encoding="utf-8") as f:
                if mode == "a":
                    f.write("\n\n---\n\n")  # Separator between runs
                f.write(cleaned)
            print(f"{'Appended to' if mode == 'a' else 'Created'} combined file: {outdata_path}")

            # Step 3: Outline with GPT (do not overwrite existing outline)
            outline_name = f"{subject}-outline.txt"
            outline_path = os.path.join(self.transcripts_dir, outline_name)
            if os.path.exists(outline_path):
                i = 1
                while os.path.exists(os.path.join(self.transcripts_dir, f"{subject}-outline-{i}.txt")):
                    i += 1
                outline_path = os.path.join(self.transcripts_dir, f"{subject}-outline-{i}.txt")
            chunks = chunk_text(cleaned)
            outlines = []
            for i, chunk in enumerate(chunks):
                print(f"Outlining chunk {i+1}/{len(chunks)} for subject {subject}...")
                try:
                    outlines.append(outline_with_gpt_text(chunk, api_key, subject))
                except openai.RateLimitError as e:
                    print("OpenAI API rate or token limit exceeded. Try splitting your transcript into smaller files or wait and try again.")
                    print(str(e))
                    return
            outline = "\n\n---\n\n".join(outlines)
            mode = "a" if os.path.exists(outline_path) else "w"
            with open(outline_path, mode, encoding="utf-8") as f:
                if mode == "a":
                    f.write("\n\n---\n\n")  # Separator between runs
                f.write(outline)
            print(f"{'Appended to' if mode == 'a' else 'Created'} outline: {outline_path}")

        print("\nAll outlines generated. Check your directory for new files.")