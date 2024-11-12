from scraper_api import ScraperAPIClient
import streamlit as st
from PIL import Image
import json
import Classifier
from Classifier import KNearestNeighbours  # We are using KNN Algorithm
from bs4 import BeautifulSoup  # used for web Scrapping
import requests
from requests import get
import io
import PIL.Image
import base64
from urllib.request import urlopen  # to open the url link

st.set_page_config(
    page_title="The Movie Suggester System",
)

# adding css to streamlit:
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# adding Background Image:
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stTitle{{
    color:"red";
    }}
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover;
    }}
    </style>
    """,
        unsafe_allow_html=True
    )

add_bg_from_local("../Movie_Final_System/bg_image.jpg")

file_ = open("./meta/logo.png", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.markdown(
    f'<img src="data:image/png;base64,{data_url}" alt="logo" style="position:absolute;top:-120px;left:250px;width:10rem;height:10rem;">',
    unsafe_allow_html=True,
)

with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

# Scraper API key
client = ScraperAPIClient('a8c7a10dde6b783d10d703fed6ea2d54')

def movie_poster_fetcher(imdb_link):
    # Call the website using sdk
    url_data = client.get(imdb_link).text

    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    movie_poster_link = imdb_dp.attrs['content']
    u = urlopen(movie_poster_link)
    raw_data = u.read()
    image = PIL.Image.open(io.BytesIO(raw_data))
    image = image.resize((158, 301), )
    st.image(image, use_column_width=False)

    # to get the title
    movie_find = s_data.find("meta", property="og:title")
    movie_name = movie_find.attrs['content']
    movie_name = str(movie_name).replace('- IMDb', '')

    # to find the movie description
    imdb_content = s_data.find("meta", property="og:description")
    movie_descr = imdb_content.attrs['content']
    movie_descr = str(movie_descr).split('.')
    movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.'

    # fetch director
    movie_director = movie_descr[0]

    # fetch cast
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()

    return movie_name, movie_director, movie_cast, movie_story

def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link)  # converting link into text
    s_data = BeautifulSoup(url_data.text, 'html.parser')  # s_data = full website data
    imdb_content = s_data.find("meta",
                               property="og:description")  # from meta we are finding property which have og: description
    movie_descr = imdb_content.attrs['content']

    movie_descr = str(movie_descr).split('.')
    movie_director = movie_descr[0]
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()
    movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.'
    rating = s_data.find("div", class_="AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3 jkCVKJ")
    rating = str(rating).split('<div class="AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3 jkCVKJ')
    rating = str(rating[1]).split("</div>")
    rating = str(rating[0]).replace(''' "> ''', '').replace('">', '')

    movie_rating = 'Total Rating count: ' + rating
    return movie_director, movie_cast, movie_story, movie_rating


def KNN_Movie_Recommender(test_point, k):  # test_point --> the movies data we have created
    # k ---> is no. of recommendations we want.
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Print list of 10 recommendations < Change value of k for a different number >
    table = []
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2], data[i][-1]])
    print(table)
    return table  # if k = 5 then return 5 recommendations, if 3 then retrun 3recommendations.

def run():
    st.markdown(
        "<span class = 'one'>The </span> <span class = 'two'>Movie </span><span class = 'three'>Suggester</span><span class = 'four'> System</span>",
        unsafe_allow_html=True)
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']
    cat_op = st.selectbox('Select Recommendation Type', category)
    if cat_op == category[0]:
        st.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Choose a movie:',
                                    ['--Select--'] + movies)
        if select_movie == '--Select--':
            st.warning('Please select Movie!!')
        else:
            no_of_reco = st.slider('Recommendations:', min_value=5, max_value=20, step=1)
            genres = data[movies.index(select_movie)]
            test_points = genres
            table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
            table.pop(0)  # popping out the selected movie itself.
            c = 0
            st.success('Have a look below at some of our recommendations!')
            for movie, link, ratings in table:
                c = c + 1  # Here initialisizing the count
                st.markdown(f"({c})[ {movie}]({link})")
                name, director, cast, story = movie_poster_fetcher(link)
                st.markdown(director)
                st.markdown(cast)
                st.markdown(story)
                # st.markdown(total_rat)
                st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Recommendations:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Have a look below at some of our recommendations!')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    name, director, cast, story = movie_poster_fetcher(link) # movie_poster_fetcher(link)
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐') # st.markdown(total_rat)
run() 
