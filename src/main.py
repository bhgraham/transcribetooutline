import sys
from analyzer import TranscriptAnalyzer

def main():
    if len(sys.argv) > 2:
        print("Usage: python src/main.py [transcripts_directory]")
        sys.exit(1)
    transcripts_dir = sys.argv[1] if len(sys.argv) == 2 else "."
    analyzer = TranscriptAnalyzer(transcripts_dir)
    analyzer.run()

if __name__ == "__main__":
    main()