# Transcript Analyzer

## Overview
The Transcript Analyzer is a Python application designed to analyze and separate transcripts from class recordings based on timestamps and class types. It detects overlaps and duplicates in the transcripts, providing a streamlined way to manage and review educational content.

## Project Structure
```
transcript-analyzer
├── src
│   ├── main.py          # Entry point of the application
│   ├── analyzer.py      # Contains the TranscriptAnalyzer class for analyzing transcripts
│   ├── parser.py        # Contains the TranscriptParser class for parsing transcript files
│   ├── utils.py         # Utility functions for various operations
│   └── types
│       └── __init__.py  # Custom types and data structures
├── requirements.txt     # Project dependencies
└── README.md            # Documentation for the project
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd transcript-analyzer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the Transcript Analyzer, execute the following command:
```
python src/main.py
```

### Main Functionalities
- **Transcript Parsing**: The application can parse transcript files to extract timestamps and class types.
- **Overlap Detection**: It identifies overlapping timestamps in the transcripts to ensure clarity in class recordings.
- **Duplicate Detection**: The analyzer checks for duplicate entries in the transcripts, helping to maintain unique records.
- **Class Separation**: Transcripts can be separated based on class types for easier navigation and review.

## Example
After running the application, you can provide a transcript file, and the analyzer will output the processed results, highlighting any overlaps or duplicates detected.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.