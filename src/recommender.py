import json
from dotenv import load_dotenv 
#load environment variables from a .env
import os #to interact with the operating system
import nltk
from nltk.tokenize import word_tokenize

try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
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
    """Extract unique skills, interests, and traits from careers.json."""
    careers = load_careers()
    skills = set()
    interests = set()
    traits = set()

    for career in careers:
        skills.update(career.get('skills', []))
        interests.update(career.get('interests', []))
        traits.update(career.get('traits', []))

    return list(skills), list(interests), list(traits)



def recommend_career(u_input):
    """recommend career based on skills, interests, traits"""
    careers = load_careers()
    recommendations = []

    for career in careers:
        skillmatches = len(set(u_input.get('skills', [])) & set(career['skills'])) #& - finds common elements

        interestmatches = len(set(u_input.get('interests', [])) & set(career['interests']))

        traitmatches = len(set(u_input.get('traits', [])) & set(career['traits']))

        #weighted
        totalscore = skillmatches * 2 + interestmatches + traitmatches

        if totalscore > 0: #at least one match
            recommendations.append({
                "career": career['career'],
                "score": totalscore,
                "description": career['description'],
                "courses": career['courses'],
                "skills": list(set(u_input.get('skills', [])) & set(career['skills'])),
                "interests": list(set(u_input.get('interests', [])) & set(career['interests'])),
                "traits": list(set(u_input.get('traits', [])) & set(career['traits']))
            })
    
            print(f"Debug: {career['career']} - Skills: {skillmatches}, Interests: {interestmatches}, Traits: {traitmatches}, Score: {totalscore}")

    #sort from score (high to low)
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations







def process_texts(text, skills_op, interests_op, traits_op):
    """process free text inputs, extract skills, interests, traits"""
    if not text:
        return{"skills": [], "interests": [], "traits": []}
    
    #tokenize text
    tokens = word_tokenize(text.lower())

    #map tokens to predefined options
    skills =[]
    interests = []
    traits = []

    for token in tokens:
        for skill in skills_op:
            if token in skill.lower(): #check if each token exist in any skill from skills_op
                skills.append(skill) #add the full skill name to skills list if matched

        for interest in interests_op:
            if token in interest.lower():
                interests.append(interest)

        for trait in traits_op:
            if token in trait.lower() or token == trait.lower().replace("-", " "): #if token matches the trait with hyphens replaced by spaces
                traits.append(trait)

    return {
        "skills": list(set(skills)),
        "interests": list(set(interests)),
        "traits": list(set(traits))
    }





if __name__ == "__main__":

    skills, interests, traits = get_ops_from_careers()

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