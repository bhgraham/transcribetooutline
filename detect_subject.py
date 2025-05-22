import os
import openai
import sys

def detect_subject(transcript_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set your OPENAI_API_KEY environment variable.")

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    prompt = (
        "You are an expert at classifying transcripts by subject. "
        "Given the following transcript, return ONLY the most likely subject as a single word or phrase. "
        "Possible subjects are law school courses (e.g., Torts, Contracts, Property, Criminal Law, Constitutional Law, Civil Procedure, Legal Writing, Professional Responsibility, Administrative Law, etc.) "
        "or 'Medical' if the transcript is about medical topics. "
        "If you are unsure, return 'Unknown'.\n\n"
        f"Transcript:\n{transcript}\n\nSubject:"
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

    subject = response.choices[0].message.content.strip()
    print(subject)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detect_subject.py <input_transcript.txt>")
        exit(1)
    detect_subject(sys.argv[1])