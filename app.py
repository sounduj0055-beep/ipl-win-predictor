import streamlit as st
import pickle
import pandas as pd
import base64

st.set_page_config(page_title="IPL Predictor", layout="wide")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/jpeg;base64,{encoded_string});
        background-size: cover;
        background-attachment: fixed;
    }}

    div[data-testid="stAppViewContainer"] > .main h1 {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }}
    div[data-testid="stAppViewContainer"] > .main .stCaption {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }}

    .stSidebar > div:first-child {{
        background-color: rgba(255, 255, 255, 0.95);
    }}
    .stSidebar * {{
        color: #0E1117 !important;
        text-shadow: none !important;
    }}

    .stApp > div[data-testid="stToolbar"], .stApp > header {{
        background-color: rgba(255, 255, 255, 0); 
    }}

    .main > div[data-testid="stBlock"] {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
    }}
    .main > div[data-testid="stBlock"] * {{
        color: #0E1117 !important; 
        text-shadow: none !important;
    }}
    
    .main > div > h1 {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }}
    
    .stButton > button {{
        color: #0E1117 !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
    )

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("IPL Win Predictor - Login")
    
    password = st.text_input("Enter Password:", type="password")
    
    if st.button("Login"):
        if password == "ipl2025":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password")

def main_app():
    try:
        pipe = pickle.load(open('pipe.pkl', 'rb'))
    except FileNotFoundError:
        st.error("Model file (pipe.pkl) not found. Please ensure it's in the same directory.")
        return
    except Exception as e:
        st.error(f"An error occurred while loading the model: {e}")
        return
        
    teams = [
        'Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
        'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
        'Rajasthan Royals', 'Delhi Capitals'
    ]
    cities = [
        'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
        'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
        'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
        'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
        'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
        'Sharjah', 'Mohali', 'Bengaluru'
    ]

    st.title('IPL Win Predictor 🏏')
    st.caption('A Machine Learning app to predict real-time match outcomes')

    st.sidebar.header('Enter Match Details')
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    batting_team = st.sidebar.selectbox('Select the batting team', sorted(teams))
    bowling_team = st.sidebar.selectbox('Select the bowling team', sorted(teams))
    selected_city = st.sidebar.selectbox('Select host city', sorted(cities))
    target = st.sidebar.number_input('Target Score', min_value=1)
    score = st.sidebar.number_input('Current Score', min_value=0)
    overs = st.sidebar.number_input('Overs completed', min_value=0.0, max_value=19.5, step=0.1, format="%.1f")
    wickets = st.sidebar.number_input('Wickets out', min_value=0, max_value=9)

    if st.button('Predict Win Probability'):
        
        if batting_team == bowling_team:
            st.error('Batting and Bowling teams cannot be the same. Please select different teams.')
        else:
            runs_left = target - score
            balls_left = 120 - (overs * 6)
            wickets_left = 10 - wickets
            crr = score / overs if overs > 0 else 0
            rrr = (runs_left * 6) / balls_left if balls_left > 0 else float('inf')

            st.subheader("Match Summary")
            summary_data = {
                "Batting Team": batting_team,
                "Bowling Team": bowling_team,
                "Match State": f"Need {runs_left} runs in {int(balls_left)} balls"
            }
            st.json(summary_data)

            if runs_left <= 0:
                st.header(f"Predicted Winner: {batting_team}")
                st.subheader(f"{batting_team} Win Probability")
                st.progress(1.0)
                st.subheader(f"{bowling_team} Win Probability")
                st.progress(0.0)
            
            elif wickets_left <= 0:
                st.header(f"Predicted Winner: {bowling_team}")
                st.subheader(f"{batting_team} Win Probability")
                st.progress(0.0)
                st.subheader(f"{bowling_team} Win Probability")
                st.progress(1.0)
            
            elif balls_left <= 0:
                st.header(f"Predicted Winner: {bowling_team}")
                st.subheader(f"{batting_team} Win Probability")
                st.progress(0.0)
                st.subheader(f"{bowling_team} Win Probability")
                st.progress(1.0)
                
            else:
                input_df = pd.DataFrame({
                    'BattingTeam': [batting_team],
                    'BowlingTeam': [bowling_team],
                    'City': [selected_city],
                    'runs_left': [runs_left],
                    'balls_left': [balls_left],
                    'wickets_left': [wickets_left],
                    'total_run_x': [target],
                    'crr': [crr],
                    'rrr': [rrr]
                })
                
                result = pipe.predict_proba(input_df)
                loss_prob = result[0][0]
                win_prob = result[0][1]

                if win_prob > 0.5:
                    st.header(f"Predicted Winner: {batting_team}")
                else:
                    st.header(f"Predicted Winner: {bowling_team}")

                st.subheader(f"{batting_team} Win Probability")
                st.progress(win_prob)
                
                st.subheader(f"{bowling_team} Win Probability")
                st.progress(loss_prob)

if st.session_state.logged_in:
    try:
        add_bg_from_local('background.jpg')
    except FileNotFoundError:
        st.warning("Background image 'background.jpg' not found. App will use default background.")
    
    main_app()
else:
    login_page()
