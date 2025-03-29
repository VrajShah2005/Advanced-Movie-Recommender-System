import base64
import pickle
import pandas as pd
import requests
import streamlit as st

# Function to fetch poster for a given movie ID
def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=415824fdedd7d788f9646c4518e669da&language=en-US'.format(
                movie_id))
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error("Error fetching poster: {}".format(e))
        return None

# Function to recommend movies similar to the selected movie
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index
    if len(movie_index) == 0:
        st.warning("Movie not found in the dataset.")
        return [], []  # Return empty lists if movie not found
    movie_index = movie_index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
            recommended_movies.append(movies.iloc[i[0]].title)
    if len(recommended_movies) < 5:
        st.warning("Only {} recommendations available.".format(len(recommended_movies)))
    return recommended_movies, recommended_movies_posters

# Load movie data and similarity scores
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)

# Set up Streamlit application
st.markdown("""
    <style>
    .stApp {
        background-color: black;
    }
    .title-text, .subtitle-text, .recommended-text {
        color: yellow;
        font-size: 20px;
        text-align: center;
    }
    .selectbox-label {
        color: yellow;
        font-size: 20px;
        text-align: left;
        margin-bottom: -30px; /* Further reduced gap */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-text" style="font-size:36px; font-weight:bold;">Movie Recommender System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text" style="font-size:20px;">Made By: Vraj Shah</p>', unsafe_allow_html=True)

st.markdown('<p class="selectbox-label" style="font-size:20px;">Select a movie:</p>', unsafe_allow_html=True)
selected_movie_name = st.selectbox('', movies['title'].values, key='select_movie')

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    num_recommendations = len(names)
    num_rows = (num_recommendations + 4) // 5  # Round up to the nearest multiple of 5
    for row in range(num_rows):
        cols = st.columns(5)  # Create 5 columns for each row
        start_index = row * 5
        end_index = min((row + 1) * 5, num_recommendations)
        for i in range(start_index, end_index):
            with cols[i % 5]:
                st.markdown(f'<p class="recommended-text">{names[i]}</p>', unsafe_allow_html=True)
                if posters[i]:
                    st.image(posters[i])
                else:
                    st.warning("Poster not found")