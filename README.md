# career_recommender
Career/Skill-Based Recommender System

A Python-based application that recommends careers based on user input of skills, interests, and traits. It processes free-text input using natural language processing (NLP) and matches it against a predefined dataset of careers stored in a JSON file.



Features (planned)

**Text Processing: Converts free-text input into structured skills, interests, and traits.
**Career Matching: Recommends careers based on matches with user input, using a weighted scoring system (skills × 2 + interests + traits).
**JSON Data: Uses a careers.json file to store career data, including descriptions, courses, skills, interests, and traits.
**Debug Output: Provides detailed debug information on match counts and scores for each career.


Requirements

Python 3.6 or higher
Required Python packages:
    nltk (for text tokenization)
    python-dotenv (for environment variable management)
A careers.json file in the data/ directory (see Data Format)


Project structure

career_recommender/
├── data/
│   └── careers.json
├── src/
│   └── recommender.py
├── app.py
├── README.md
├── requirements.txt
└── .env