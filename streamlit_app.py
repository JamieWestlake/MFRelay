import random
import time
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Suit symbols
SUITS = ['♠️', '❤️', '♦️', '♣️']

# Opening label mapping
OPENING_LABELS = {
    "1C": f"1{SUITS[3]}",
    "1D": f"1{SUITS[2]}",
    "1H": f"1{SUITS[1]}",
    "1S": f"1{SUITS[0]}",
}
ORDERED_CODES = ["1C", "1D", "1H", "1S"]

# Load the database safely
df = pd.read_csv("Data/Database MF Relay.csv", encoding="utf-8-sig")
df.columns = df.columns.str.strip()  # Clean header spaces

# Replace placeholders like {SUITS[3]} with actual suit symbols
df['Bidding Sequences'] = df['Bidding Sequences'].str.replace("{SUITS[0]}", "♠️")
df['Bidding Sequences'] = df['Bidding Sequences'].str.replace("{SUITS[1]}", "❤️")
df['Bidding Sequences'] = df['Bidding Sequences'].str.replace("{SUITS[2]}", "♦️")
df['Bidding Sequences'] = df['Bidding Sequences'].str.replace("{SUITS[3]}", "♣️")

# Now parse the 'Shape' column properly
df['Shape'] = df['Shape'].apply(lambda x: list(map(int, x.strip('[]').split(','))))

# Extract columns
bidding_sequences = df['Bidding Sequences'].tolist()
families = df['Shape'].tolist()
openings = df['Opening'].tolist()
answers = list(zip(df['Shape'], df['Strength']))
ClubSlam = df['ClubSlam'].tolist()
DiamondSlam = df['DiamondSlam'].tolist()
HeartSlam = df['HeartSlam'].tolist()
SpadeSlam = df['SpadeSlam'].tolist()
HeartGame = df['HeartGame'].tolist()
SpadeGame = df['SpadeGame'].tolist()
ClubGame = df['ClubGame'].tolist()
DiamondGame = df['DiamondGame'].tolist()

st.title("\U0001F0CF MancheForcing Relay Trainer")

main_col, right_sidebar = st.columns([5, 1])

with main_col:
    st.sidebar.header("\U0001F3AF Filters")

    selected_sections = st.sidebar.multiselect(
        "Sections to answer:",
        options=["Bidding Info", "Slam Bidding", "Game Bidding"],
        default=["Bidding Info", "Slam Bidding", "Game Bidding"]
    )

    unique_families = list({tuple(fam) for fam in families})
    selected_families = st.sidebar.multiselect("Family:", unique_families, default=unique_families)

    available_codes = [code for code in ORDERED_CODES if code in openings]
    available_labels = [OPENING_LABELS[code] for code in available_codes]
    selected_labels = st.sidebar.multiselect("Opening:", options=available_labels, default=available_labels)
    selected_codes = [code for code, label in OPENING_LABELS.items() if label in selected_labels]

    filtered_indices = [
        i for i in range(len(bidding_sequences))
        if tuple(families[i]) in selected_families and openings[i] in selected_codes
    ]

    if not filtered_indices:
        st.error("No bidding sequences match your filters. Please adjust them.")
        st.stop()

    if "random_index" not in st.session_state or st.session_state.random_index not in filtered_indices:
        st.session_state.random_index = random.choice(filtered_indices)
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "correct_count" not in st.session_state:
        st.session_state.correct_count = 0
    if "attempted_count" not in st.session_state:
        st.session_state.attempted_count = 0
    if "total_time" not in st.session_state:
        st.session_state.total_time = 0.0
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    def new_hand():
        st.session_state.random_index = random.choice(filtered_indices)
        st.session_state.submitted = False
        st.session_state.start_time = time.time()

    if st.button("\U0001F504 Full Reset"):
        st.session_state.random_index = random.choice(filtered_indices)
        st.session_state.submitted = False
        st.session_state.correct_count = 0
        st.session_state.attempted_count = 0
        st.session_state.total_time = 0.0
        st.session_state.start_time = time.time()

    index = st.session_state.random_index
    sequence = bidding_sequences[index]
    correct_distribution, correct_type = answers[index]

    st.markdown("### Bidding Sequence:")
    st.write(sequence)

    if "Bidding Info" not in selected_sections:
        st.markdown("**Bidding Info (for reference):**")
        st.write(f"Distribution: {correct_distribution} ({correct_type})")

    if not st.session_state.submitted:
        with st.form(key="answer_form"):
            cols = st.columns([2, 2, 2])
            col1, col2, col3 = cols

            with col1:
                if "Bidding Info" in selected_sections:
                    st.markdown("### \U0001F9EE Bidding Info")
                    user_input = st.text_input("Enter distribution as 4 digits (♠️♥️♦️♣️):", max_chars=4)
                    user_type = st.radio("Select type:", ["min", "max"], horizontal=True)
                else:
                    user_input = user_type = None

            with col2:
                if "Slam Bidding" in selected_sections:
                    st.markdown("### \U0001F3AF Slam Bidding")
                    user_club_slam = st.text_input("♣️ Club Slam", key="club_slam")
                    user_diamond_slam = st.text_input("♦️ Diamond Slam", key="diamond_slam")
                    user_heart_slam = st.text_input("♥️ Heart Slam", key="heart_slam")
                    user_spade_slam = st.text_input("♠️ Spade Slam", key="spade_slam")
                else:
                    user_club_slam = user_diamond_slam = user_heart_slam = user_spade_slam = None

            with col3:
                if "Game Bidding" in selected_sections:
                    st.markdown("### \U0001F3C6 Game Bidding")
                    user_heart_game = st.radio("♥️ Heart Game (4H?)", ["Yes", "No"], horizontal=True)
                    user_spade_game = st.radio("♠️ Spade Game (4S?)", ["Yes", "No"], horizontal=True)
                    user_club_game = st.radio("♣️ Club Game (5C?)", ["Yes", "No"], horizontal=True)
                    user_diamond_game = st.radio("♦️ Diamond Game (5D?)", ["Yes", "No"], horizontal=True)
                else:
                    user_heart_game = user_spade_game = user_club_game = user_diamond_game = None

            submit = st.form_submit_button("Submit")

        if submit:
            end_time = time.time()
            time_taken = end_time - st.session_state.start_time
            st.session_state.total_time += time_taken
            st.session_state.attempted_count += 1

            distribution_ok = slam_ok = game_ok = True

            if "Bidding Info" in selected_sections:
                distribution_ok = False
                if user_input and len(user_input) == 4 and user_input.isdigit():
                    user_dist = [int(d) for d in user_input]
                    possible = [(answers[i][0], answers[i][1]) for i, seq in enumerate(bidding_sequences) if seq == sequence]
                    distribution_ok = any(user_dist == dist and user_type == kind for dist, kind in possible)
                else:
                    st.warning("Please enter exactly 4 digits.")
                    st.session_state.attempted_count -= 1
                    st.session_state.total_time -= time_taken
                    st.session_state.submitted = True
                    st.stop()

            if "Slam Bidding" in selected_sections:
                def slam_match(user_val, correct_val):
                    return (
                        (correct_val == 'N.v.t.' and (not user_val or user_val.strip().lower() == "no"))
                        or (user_val.strip() == correct_val)
                    )
                slam_ok = (
                    slam_match(user_club_slam, ClubSlam[index]) and
                    slam_match(user_diamond_slam, DiamondSlam[index]) and
                    slam_match(user_heart_slam, HeartSlam[index]) and
                    slam_match(user_spade_slam, SpadeSlam[index])
                )

            if "Game Bidding" in selected_sections:
                def yn_to_val(val, expected):
                    return (val == "Yes" and expected != 'N.v.t.') or (val == "No" and expected == 'N.v.t.')
                game_ok = (
                    yn_to_val(user_heart_game, HeartGame[index]) and
                    yn_to_val(user_spade_game, SpadeGame[index]) and
                    yn_to_val(user_club_game, ClubGame[index]) and
                    yn_to_val(user_diamond_game, DiamondGame[index])
                )

            if distribution_ok and slam_ok and game_ok:
                st.success("\u2705 Correct!")
                st.session_state.correct_count += 1
            else:
                st.error("\u274C Incorrect.")
                st.markdown("**Correct Answers:**")
                st.write(f"Distribution: {correct_distribution} ({correct_type})")
                st.write(f"Club Slam: {ClubSlam[index]}")
                st.write(f"Diamond Slam: {DiamondSlam[index]}")
                st.write(f"Heart Slam: {HeartSlam[index]}")
                st.write(f"Spade Slam: {SpadeSlam[index]}")
                st.write(f"Heart Game: {'Yes' if HeartGame[index] != 'N.v.t.' else 'No'}")
                st.write(f"Spade Game: {'Yes' if SpadeGame[index] != 'N.v.t.' else 'No'}")
                st.write(f"Club Game: {'Yes' if ClubGame[index] != 'N.v.t.' else 'No'}")
                st.write(f"Diamond Game: {'Yes' if DiamondGame[index] != 'N.v.t.' else 'No'}")

            st.session_state.submitted = True

    if st.session_state.submitted:
        col1, _, _ = st.columns([2, 1, 1])
        with col1:
            st.button("Next Hand ▶️", on_click=new_hand)

with right_sidebar:
    if st.session_state.submitted:
        st.markdown("### \U0001F4CA Your Stats:")
        if st.session_state.attempted_count > 0:
            accuracy = (st.session_state.correct_count / st.session_state.attempted_count) * 100
            avg_time = (st.session_state.total_time / st.session_state.attempted_count)
        else:
            accuracy, avg_time = 0.0, 0.0

        st.metric("Score", f"{st.session_state.correct_count}/{st.session_state.attempted_count}", delta=f"{accuracy:.1f}%")
        st.metric("Avg time/hand", f"{avg_time:.2f}s")
