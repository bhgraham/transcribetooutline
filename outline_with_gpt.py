import os
import openai

def outline_transcript(transcript_path, output_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set your OPENAI_API_KEY environment variable.")

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    prompt = (
        "You are an expert legal educator. "
        "Take the following transcript and turn it into a clear, organized outline. "
        "Use headings and bullet points. Focus on the main topics, subtopics, and key details. "
        "Do not include extraneous information. Here is the transcript:\n\n"
        f"{transcript}"
    )

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4-1106-preview"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0.3,
    )

    outline = response.choices[0].message.content

    # If the output file exists, append; otherwise, write new
    mode = "a" if os.path.exists(output_path) else "w"
    with open(output_path, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n\n---\n\n")  # Separator between outlines
        f.write(outline)
    print(f"Outline {'appended to' if mode == 'a' else 'saved to'} {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python outline_with_gpt.py <input_transcript.txt> <output_outline.txt>")
        exit(1)
    outline_transcript(sys.argv[1], sys.argv[2])