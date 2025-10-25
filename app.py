import streamlit as st
import pickle
import pandas as pd

# Load the trained model
pipe = pickle.load(open('pipe.pkl', 'rb'))

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

st.title('IPL Win Predictor')

# Create columns for layout
col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox('Select the batting team', sorted(teams))
with col2:
    bowling_team = st.selectbox('Select the bowling team', sorted(teams))

# Get the city where the match is played
selected_city = st.selectbox('Select host city', sorted(cities))

# Get the target score
target = st.number_input('Target', min_value=1)

# Create more columns for the current match state
col3, col4, col5 = st.columns(3)

with col3:
    score = st.number_input('Score', min_value=0)
with col4:
    overs = st.number_input('Overs completed', min_value=0.0, max_value=19.5, step=0.1, format="%.1f")
with col5:
    wickets = st.number_input('Wickets out', min_value=0, max_value=9)

# The "Predict" button
if st.button('Predict Probability'):
    runs_left = target - score
    balls_left = 120 - (overs * 6)
    wickets_left = 10 - wickets
    crr = score / overs if overs > 0 else 0
    rrr = (runs_left * 6) / balls_left if balls_left > 0 else float('inf')

    # Create a DataFrame from the inputs
    input_df = pd.DataFrame({
        'BattingTeam': [batting_team],
        'BowlingTeam': [bowling_team],
        'City': [selected_city],
        'runs_left': [runs_left],
        'balls_left': [balls_left],
        'wickets_left': [wickets_left],
        'total_runs_x': [target], # Using the correct column name from your training
        'crr': [crr],
        'rrr': [rrr]
    })
    
    # Make a prediction
    result = pipe.predict_proba(input_df)
    win_prob = result[0][1]
    loss_prob = result[0][0]

    # Display the results
    st.header(f"{batting_team} - {round(win_prob * 100)}%")
    st.header(f"{bowling_team} - {round(loss_prob * 100)}%")