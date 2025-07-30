import streamlit as st
from src.recommender import recommend_career, get_ops_from_careers, process_texts

st.set_page_config(page_title="Career Recommender")
st.title("Career Recommender System")
st.markdown("""Describe your skills, interests, and traits in your own words or select from the dropdowns to get personalized career recommendations.""")

skills_options, interests_options, traits_options = get_ops_from_careers()

with st.form("u_input"):
    st.subheader("Your Details")
    free_text = st.text_area("Describe your skills, interests, and traits (e.g., 'I like coding, math, and being creative')", 
                             help="Enter a sentence or keywords about what you know or enjoy.")
    
    skills = st.multiselect("Or select skills", sorted(skills_options), help="Choose skills you have or want to develop.")

    interests = st.multiselect("Or select interests", sorted(interests_options), help="Pick areas you enjoy.")

    traits = st.multiselect("Or select traits", sorted(traits_options), help="Select traits that describe you.")

    submit = st.form_submit_button("Get Recommendations")

    