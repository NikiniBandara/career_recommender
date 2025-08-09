import json
from dotenv import load_dotenv 
#load environment variables from a .env
import os #to interact with the operating system
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer #lemmatization
from fuzzywuzzy import fuzz

try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('wordnet', quiet=True) #lemmatization
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")



load_dotenv()
DATA_PATH = os.getenv("DATA_PATH", "data/careers.json")
#if no .env file default to 'careers.json'

def load_careers():
    """Load careers from JSON file."""
    
    with open(DATA_PATH, 'r') as f:
        return json.load(f) #parse JSON file (f) into a Python object


"""
def display_careers():
    careers = load_careers()
    for career in careers:
        print(f"Career: {career['career']}")
        print(f"Description: {career['description']}")
        print(f"Courses: {', '.join(career['courses'])}")
        print(f"Skills: {', '.join(career['skills'])}")
        print(f"Interests: {', '.join( career['interests'])}")
        print(f"Traits: {', '.join(career['traits'])}") 
"""

def get_ops_from_careers(): #getting the lists of skills, interests and traits from the existing data (form all careers)
    """Extract unique skills, interests, traits and fields from careers.json."""
    careers = load_careers()
    skills = set()
    interests = set()
    traits = set()
    fields = set()

    for career in careers:
        skills.update(career.get('skills', []))
        interests.update(career.get('interests', []))
        traits.update(career.get('traits', []))
        fields.add(career.get('field', 'other')) #default to 'other'

    return list(skills), list(interests), list(traits), list(fields)



def recommend_career(u_input, min_score=2, fields=None):
    """recommend career based on skills, interests, traits"""
    careers = load_careers()
    recommendations = []

    skill_weight = 2
    interest_weight = 1
    trait_weight = 1

    print(f"Received fields: {fields}")  # Debug
    for career in careers:
        career_field = career.get('field', 'other')
        print(f"Checking career: {career['career']}, Field: {career_field}, Selected fields: {fields}")

        #If fields exists and is non-empty - and - If the career's field is NOT in fields
        #if fields and career.get('field', 'other') not in fields: 

        if fields and career_field not in fields:
            print(f"Skipping {career['career']} (field: {career_field})")
            continue #If both conditions are true, the career is skipped

        skillmatches = len(set(u_input.get('skills', [])) & set(career['skills'])) #& - finds common elements

        interestmatches = len(set(u_input.get('interests', [])) & set(career['interests']))

        traitmatches = len(set(u_input.get('traits', [])) & set(career['traits']))

        #weighted
        total_score = skillmatches * skill_weight + interestmatches * interest_weight + traitmatches * trait_weight

        if total_score >= min_score: #at least one match
            recommendations.append({
                "career": career['career'],
                "score": total_score,
                "description": career['description'],
                "courses": career['courses'],
                "skills": list(set(u_input.get('skills', [])) & set(career['skills'])),
                "interests": list(set(u_input.get('interests', [])) & set(career['interests'])),
                "traits": list(set(u_input.get('traits', [])) & set(career['traits'])),
                "field": career.get('field', 'Other')
            })
    
            print(f"Debug: {career['career']} - Skills: {skillmatches}, Interests: {interestmatches}, Traits: {traitmatches}, Score: {total_score}")

    #sort from score (high to low)
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations







def process_texts(text, skills_op, interests_op, traits_op):
    """process free text inputs, extract skills, interests, traits"""
    if not text:
        return{"skills": [], "interests": [], "traits": []}
    
    lemmatizer = WordNetLemmatizer()
    #tokenize text
    #tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token.lower()) for token in word_tokenize(text.lower())]

    #map tokens to predefined options
    skills =[]
    interests = []
    traits = []

    FUZZY_THRESHOLD = 80  # Similarity score threshold (0-100)

    for token in tokens:
        for skill in skills_op:
            #if token in skill.lower(): #check if each token exist in any skill from skills_op
            skill_lower = lemmatizer.lemmatize(skill.lower()) #Lemmatizes it (reduces to base/dictionary form, ex: "running" → "run")
            if (token in skill_lower or fuzz.ratio(token, skill_lower) >= FUZZY_THRESHOLD or
                fuzz.partial_ratio(token, skill_lower) >= FUZZY_THRESHOLD):
             
                skills.append(skill) #add the full skill name to skills list if matched

        for interest in interests_op:
            #if token in interest.lower():
            interest_lower = lemmatizer.lemmatize(interest.lower())
            if (token in interest_lower or fuzz.ratio(token, interest_lower) >= FUZZY_THRESHOLD or
                fuzz.partial_ratio(token, interest_lower) >= FUZZY_THRESHOLD):

                interests.append(interest)

        for trait in traits_op:
            #if token in trait.lower() or token == trait.lower().replace("-", " "): #if token matches the trait with hyphens replaced by spaces
            trait_lower = lemmatizer.lemmatize(trait.lower())
            if (token in trait_lower or token == trait_lower.replace("-", " ") or
                fuzz.ratio(token, trait_lower) >= FUZZY_THRESHOLD or
                fuzz.partial_ratio(token, trait_lower) >= FUZZY_THRESHOLD):
             #.lower() Converts the trait to lowercase
                traits.append(trait)



    return {
        "skills": list(set(skills)),
        "interests": list(set(interests)),
        "traits": list(set(traits))
    }

"""
Lowercasing: text.lower() ensures case-insensitive matching.
Tokenization: word_tokenize() splits the text into individual words/tokens.
Lemmatization: WordNetLemmatizer() reduces words to their base/dictionary form
"""




if __name__ == "__main__":

    skills, interests, traits, fields = get_ops_from_careers()

    # Test 
    free_text = "I like coding, math"
    u_input = process_texts(free_text, skills, interests, traits)
    print("Processed Input:", u_input)

    recommendations = recommend_career(u_input)
    for rec in recommendations:
        print(f"Career: {rec['career']} (Score: {rec['score']})")
        print(f"Description: {rec['description']}")
        print(f"Courses: {', '.join(rec['courses'])}")
        print(f"Matched Skills: {', '.join(rec['skills'])}")
        print(f"Matched Interests: {', '.join(rec['interests'])}")
        print(f"Matched Traits: {', '.join(rec['traits'])}")
        print(' ')
