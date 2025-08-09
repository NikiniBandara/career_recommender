import streamlit as st
import plotly.graph_objects as go
import json
from src.recommender import recommend_career, get_ops_from_careers, process_texts

st.set_page_config(page_title="Career Recommender", layout="wide")
st.title("Career Recommender System")
st.markdown("""Describe your skills, interests, and traits in your own words or select from the dropdowns to get personalized career recommendations.""")

#custom CSS for background 
css = """
<style>
/* Set background image for the entire app */
.stApp {
    background-image: url("https://www.flexjobs.com/blog/wp-content/uploads/2022/10/19070942/TED-Talk-What-Is-YOUR-Definition-of-Success.jpg?w=1024");
    
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Set white font color for most text elements, excluding buttons and dropdowns */
body, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, .stTextInput > label, .stSlider > label {
    color: white !important;
}



/* Dark gray background for sections (form, expanders, alerts) with high specificity */
div[data-testid="stForm"], div[data-testid="stExpander"], div.stMarkdown, div[data-testid="stAlert"], div[data-testid="stSpinner"] {
    background-color: #2E2E2E !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* Style buttons text to black with comprehensive selectors */
button[data-testid="stFormSubmitButton"], button[data-testid="baseButton-primary"], button[data-testid="baseButton-secondary"], button[data-testid="baseButton-tertiary"], button[class*="stButton"], button[class*="stDownloadButton"], div.stButton button, div[data-testid="stForm"] button, div[data-testid="stDownloadButton"] button {
    background-color: #000000 !important; /* Black text */
    
}

/* Style Plotly chart text for white color */
div.plotly-graph-div text, div.plotly-graph-div .plotly-html-element {
    fill: white !important;
    color: white !important;
}

/* Plotly chart background matches sections */
div.plotly-graph-div {
    background-color: #2E2E2E !important; /* Dark gray shade of black */
}

</style>
"""

st.markdown(css, unsafe_allow_html=True)

#from existing data - load 
try:
    skills_options, interests_options, traits_options, fields_options = get_ops_from_careers()
    st.write(f"Debug: Available field options: {fields_options}")  # Debug field options
except Exception as e:
    st.error(f"Failed to load career data: {e}")
    st.stop()

#initialize session state
#Without this, the recommendations would disappear every time the app rerun
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'profile_to_download' not in st.session_state:
    st.session_state.profile_to_download = None
if 'form_reset_key' not in st.session_state:
    st.session_state.form_reset_key = 0

#user_profile: Stores the current user’s inputs (skills, interests, traits, fields, free text, and minimum score).
#profile_to_download: Stores the profile data ready to be downloaded as a JSON file.
#form_reset_key: A counter used to reset the form when a profile is loaded or reset, ensuring the UI updates correctly.


#Load profile -json file
st.subheader("Load Saved Profile")
uploaded_file = st.file_uploader("Upload a saved profile (JSON)", type="json", key=f"uploader_{st.session_state.form_reset_key}")
#if the key changes, the widget resets
if uploaded_file:
    try:
        uploaded_file.seek(0)  # Reset file pointer
        profile_data = json.load(uploaded_file)
        # Validate profile structure
        expected_keys = {"free_text", "skills", "interests", "traits", "fields", "min_score"}
        if not all(key in profile_data for key in expected_keys):
            raise ValueError("Invalid profile structure: missing required keys")
        

        st.session_state.user_profile = profile_data
        st.session_state.form_reset_key += 1  # Trigger form refresh
        st.success("Profile loaded successfully!")
        st.session_state.profile_to_download = None  # Clear previous download data
        st.rerun()  #Refresh the app to update the form with the loaded profile’s values.
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Failed to load profile: {str(e)}")



#get user input
with st.form(key=f"form_{st.session_state.form_reset_key}", clear_on_submit=False):    
    st.subheader("Your Details")
    free_text = st.text_area("Describe your skills, interests, and traits (e.g., 'I like coding, math, and being creative')", 
                             value=st.session_state.user_profile.get("free_text", ""),
                             help="Enter a sentence or keywords about what you know or enjoy.")
    
    skills = st.multiselect("Or select skills", sorted(skills_options),default=st.session_state.user_profile.get("skills", []),
                             help="Choose skills you have or want to develop.")

    interests = st.multiselect("Or select interests", sorted(interests_options), default=st.session_state.user_profile.get("interests", []),
                                help="Pick areas you enjoy.")

    traits = st.multiselect("Or select traits", sorted(traits_options),default=st.session_state.user_profile.get("traits", []),
                             help="Select traits that describe you.")

    fields = st.multiselect("Filter by career field", sorted(fields_options),default=st.session_state.user_profile.get("fields", []),
                             help="Choose fields to narrow down recommendations.")

    st.subheader("Customize Recommendation Weights")
    min_score = st.slider("Minimum Match Score", min_value=1.0, max_value=10.0, 
                          value=st.session_state.user_profile.get("min_score", 2.0), 
                          step=0.5,
        help="Set the minimum score for a career to be recommended. Higher values return fewer, stronger matches.")



# buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.form_submit_button("Get Recommendations")
    with col2:
        reset = st.form_submit_button("Reset")
    with col3:
        save_profile = st.form_submit_button("Save Profile")




    if submit:
        # Use loaded profile if no new inputs are provided
        #Raw Combined Inputs
        user_inputs = {
            "skills": skills or st.session_state.user_profile.get("skills", []),
            "interests": interests or st.session_state.user_profile.get("interests", []),
            "traits": traits or st.session_state.user_profile.get("traits", []),
            "fields": fields or st.session_state.user_profile.get("fields", []),
            "free_text": free_text or st.session_state.user_profile.get("free_text", "")
        }

        #if not free_text and not skills and not interests and not traits:
        #    st.error("Please give at least one input")

        if not user_inputs["free_text"] and not user_inputs["skills"] and not user_inputs["interests"] and not user_inputs["traits"]:
            st.error("Please give at least one input")

        else:
            text_in = process_texts(user_inputs["free_text"], skills_options, interests_options, traits_options) #calling process_texts() from recommender.py

            #Processed/Refined Inputs
            user_in = {
                "skills": list(set(text_in["skills"] + user_inputs["skills"])),
                "interests": list(set(text_in["interests"] + user_inputs["interests"])),
                "traits": list(set(text_in["traits"] + user_inputs["traits"]))
            }

            with st.spinner("Finding recommendations"):
                st.session_state.recommendations = recommend_career(user_in, min_score, user_inputs["fields"])

            #skills, interests, traits, fields, free_text: These are the current user inputs from form fields

            #st.session_state.user_profile: A dictionary storing a previously loaded/saved user profile (from JSON upload)
            #st.session_state.recommendations: Stores the output of recommend_career() (likely a list of career suggestions with scores)

            #text_in: Output of process_texts(), which extracts skills/interests/traits from the free-text input (free_text)
            #user_inputs: A dictionary combining new inputs and fallback values from the saved profile
            #user_in: Final combined input for the recommendation system

    if reset:
        st.session_state.recommendations = []
        st.session_state.user_profile = {}
        st.session_state.profile_to_download = None
        st.session_state.form_reset_key += 1  # Trigger form refresh
        st.rerun()

    if save_profile:
        profile = {
            "free_text": free_text,
            "skills": skills,
            "interests": interests,
            "traits": traits,
            "fields": fields,
            "min_score": min_score
        }
        st.session_state.user_profile = profile
        st.session_state.profile_to_download = profile  # Store for download outside form
        st.success("Profile saved! Download available below.")

# Download profile button (outside form)
if st.session_state.get('profile_to_download') is not None:    #download button appears only if profile_to_download exists
    st.download_button(
        label="Download Profile",
        data=json.dumps(st.session_state.profile_to_download, indent=2), #convert profile_to_download to a JSON string using json.dumps with indent=2 for readability
        file_name="user_profile.json",
        mime="application/json" #set the file type to JSON
    )    
        




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


st.subheader("Compare recommendations")
if st.session_state.recommendations:
    # Create Plotly bar chart for scores inside an expander
        with st.expander("View Career Recommendation Scores Chart"):
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=[rec["career"] for rec in st.session_state.recommendations],
                        y=[rec["score"] for rec in st.session_state.recommendations],
                        marker_color=["#9CFF9F", "#9FD4FF", "#FFCF86", "#FA8B83", "#EC7EFF", "#9CFF9F", "#9FD4FF", "#FFCF86", "#FA8B83", "#EC7EFF"][:len(st.session_state.recommendations)],
                        marker_line_color=["#94FF9A", "#82C1FF", "#FFC993", "#FF8E8E", "#DA83FF", "#94FF9A", "#82C1FF", "#FFC993", "#FF8E8E", "#DA83FF"][:len(st.session_state.recommendations)],
                        marker_line_width=1,
                        text=[rec["score"] for rec in st.session_state.recommendations],  # Display score on bars
                        textposition="auto"
                    )
                ]
            )
            fig.update_layout(
                title="Career Recommendation Scores",
                xaxis_title="Career",
                yaxis_title="Score",
                yaxis=dict(range=[0, max([rec["score"] for rec in st.session_state.recommendations], default=1) + 1]), # y-axis range from 0 to just above the maximum score in the recommendations
                showlegend=False, #hide the legend since there's only one data series
                
                title_font_color="white",
                xaxis_title_font_color="white",
                yaxis_title_font_color="white",
                xaxis_tickfont_color="white",
                yaxis_tickfont_color="white",
                paper_bgcolor="#2E2E2E",
                plot_bgcolor="#2E2E2E"
            )
            st.plotly_chart(fig, use_container_width=True)
            #display the chart in Streamlit
            #fig: The Plotly figure object we configured
            #use_container_width=True: Makes the chart expand to fill the available width
            

