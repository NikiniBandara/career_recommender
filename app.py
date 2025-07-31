import streamlit as st
from src.recommender import recommend_career, get_ops_from_careers, process_texts

st.set_page_config(page_title="Career Recommender")
st.title("Career Recommender System")
st.markdown("""Describe your skills, interests, and traits in your own words or select from the dropdowns to get personalized career recommendations.""")

#from existing data
skills_options, interests_options, traits_options = get_ops_from_careers()

#Without this, the recommendations would disappear every time the app rerun
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

#get user input
with st.form("u_input"):
    st.subheader("Your Details")
    free_text = st.text_area("Describe your skills, interests, and traits (e.g., 'I like coding, math, and being creative')", 
                             help="Enter a sentence or keywords about what you know or enjoy.")
    
    skills = st.multiselect("Or select skills", sorted(skills_options), help="Choose skills you have or want to develop.")

    interests = st.multiselect("Or select interests", sorted(interests_options), help="Pick areas you enjoy.")

    traits = st.multiselect("Or select traits", sorted(traits_options), help="Select traits that describe you.")

    st.subheader("Customize Recommendation Weights")
    min_score = st.slider("Minimum Match Score", min_value=1.0, max_value=10.0, value=2.0, step=0.5,
        help="Set the minimum score for a career to be recommended. Higher values return fewer, stronger matches.")

    submit = st.form_submit_button("Get Recommendations")

    if submit:
        if not free_text and not skills and not interests and not traits:
            st.error("Please give at least one input")
        else:
            text_in = process_texts(free_text, skills_options, interests_options, traits_options) #calling process_texts() from recommender.py

            user_in = {
                "skills": list(set(text_in["skills"] + skills)),
                "interests": list(set(text_in["interests"] + interests)),
                "traits": list(set(text_in["traits"] + traits))
            }

            with st.spinner("Finding recommendations"):
                st.session_state.recommendations = recommend_career(user_in)


#display recommendations
if st.session_state.recommendations:
    st.subheader("Recommendations for you")
    for rec in st.session_state.recommendations:
        with st.expander(f"{rec['career']} (Score: {rec['score']})"): #a clickable dropdown box for each career recommendation
            st.write(f"**Description**: {rec['description']}")
            st.write(f"**Courses**: {', '.join(rec['courses'])}")
            st.write(f"**Matched Skills**: {', '.join(rec['skills']) or 'None'}")
            st.write(f"**Matched Interests**: {', '.join(rec['interests']) or 'None'}")
            st.write(f"**Matched Traits**: {', '.join(rec['traits']) or 'None'}")
        
else:
    st.info("No recommendations yet")