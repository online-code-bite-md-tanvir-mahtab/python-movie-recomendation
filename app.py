from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import requests
import uuid

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviereco.db'

db = SQLAlchemy(app)

isLogedIn = 0
index_count = 0
user_my_id = 0

# db.create_all()


def isAuthenticated(u_pass, u_email):
    global user_my_id
    isAuth = False
    main_url = 'http://127.0.0.1:5000/login'
    param = {
        "email": u_email,
        "password":u_pass
    }
    response = requests.post(url=main_url,json=param)
    
    if response.status_code == 200:
        data = response.json()
        uid = data['userId']
        user_my_id =  uid
        isAuth = True
        _isLogedIn(user_id=uid)
    return isAuth


def isRegisterd(u_name, u_email, u_phone, u_password):
    urls = 'http://127.0.0.1:5000/signup'
    body = {
        "name": u_name,
        "email": u_email,
        "phone": u_phone,
        "password": u_password
    }
    response = requests.post(url=urls, json=body)
    news = response
    print(news.json())
    if news.status_code == 200:
        print("responded")
        return True
    else:
        return False


def _isLogedIn(user_id):
    global isLogedIn
    body = {
        "user_id":user_id
    }
    main_url = f'http://127.0.0.1:5000/is_logged_in'
    response = requests.post(url=main_url, json=body)
    news = response.json()
    if news['logged_in'] == True:
        isLogedIn = 1
    else:
        isLogedIn = 0





@app.route('/')
def home():
    return render_template('index.html', loged=isLogedIn)


@app.route('/login', methods=['POST', 'GET'])
def login():
    user_data = pd.read_csv('user_data.csv')
    if request.method == 'POST':
        password = request.form.get("full-pass")
        email = request.form.get('email')
        result = isAuthenticated(password, email)
        if result:
            return redirect('/')
        else:
            return redirect('/registration')
    return render_template('login.html')


@app.route('/registration', methods=['POST', 'GET'])
def signUp():
    print(request.method)
    user_data = pd.read_csv('user_data.csv')
    if request.method == 'POST':
        name = request.form.get('full-name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('full-pass')

        if isRegisterd(name, email, phone, password):
            if user_data.empty:
                return redirect('/login')
            else:
                return redirect('/login')
        else:
            return render_template('signup.html')
    return render_template('signup.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        user_id = user_my_id
        if user_my_id != 0:
            print(user_id)
            # Make a POST request to the provided API
            api_url = 'http://127.0.0.1:5000/logout'  # Update with your API URL
            payload = {"user_id": user_id}
            response = requests.post(api_url, json=payload)

            # Check the response status code
            if response.status_code == 200:
                # Successfully logged out, redirect to login page
                return redirect('/login')
            else:
                # Logout failed, handle accordingly
                return "Logout failed"
        else:
            return "Invalid user ID"
    else:
        return "Only POST requests are allowed for logout"
    


@app.route('/movies', methods=['GET', 'POST'])
def movies():
    url = "https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies"

    response = requests.get(url)
    movies_to_search = response.json()['movies']
    print(movies_to_search)
    user_data = pd.read_csv('user_data.csv')
    data = pd.DataFrame(movies_to_search)
    if isLogedIn == 0:
        return render_template('movies.html', movie_data=data, index=100, msg='found', loged=isLogedIn)
    else:

        if request.method == 'POST':
            search_name = request.form.get('email')
            # print()
            print(f"my value:{search_name}is")
            print(data['name'][0]+"h")
            searched_data = data[data['name'] ==
                                 search_name].reset_index(drop=True)
            print(f"search found: {len(searched_data)}")
            if len(searched_data) == 0:
                if user_data.empty:
                    return redirect('login')
                else:
                    return render_template('movies.html', movie_data=data, index=0, msg='no', loged=isLogedIn)
            else:
                return render_template('movies.html', movie_data=searched_data, index=100, msg='found', loged=isLogedIn)
        else:
            return render_template('movies.html', movie_data=data, index=100, msg='found', loged=isLogedIn)


@app.route('/recomend', methods=['GET', 'POST'])
def recomend():
    try:
        # Load the dataset
        data = pd.read_csv('mymoviedb.csv', lineterminator='\n')
        # user_data = pd.read_csv('user_data.csv')
        if isLogedIn == 0:
            redirect('/login')
        else:
            if request.method == 'POST':

                # Create TF-IDF vectorizer
                tfidf = TfidfVectorizer(stop_words='english')

                # Compute TF-IDF matrix
                tfidf_matrix = tfidf.fit_transform(data['Overview'].fillna(''))

                # Compute cosine similarity matrix
                cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

                # Function to get movie recommendations based on content similarity
                def get_content_based_recommendations(title, cosine_sim=cosine_sim, data=data, top_n=5):
                    # Convert all titles and the search term to lowercase for case-insensitive matching
                    data['Title_lower'] = data['Title'].str.lower()
                    title_lower = title.lower()

                    # Find titles containing the search term
                    matching_titles = data[data['Title_lower'].str.contains(
                        title_lower, na=False)]

                    # If there are no matching titles, return an empty DataFrame
                    if matching_titles.empty:
                        return pd.DataFrame(columns=['Title', 'Release_Date', 'Popularity', 'Overview', 'Poster_Url'])

                    # Use the first matching title for recommendations (you can modify this logic based on your requirements)
                    first_matching_title = matching_titles.iloc[0]

                    # Get the index of the matching title
                    idx = data[data['Title_lower'] ==
                               first_matching_title['Title_lower']].index[0]

                    scores = list(enumerate(cosine_sim[idx]))
                    scores = sorted(scores, key=lambda x: x[1], reverse=True)
                    top_scores = scores[1:top_n+1]
                    movie_indices = [i[0] for i in top_scores]

                    return data[['Title', 'Release_Date', 'Popularity', 'Overview', 'Poster_Url']].iloc[movie_indices]

                # Get content-based recommendations for a movie
                movie_title = request.form.get('email')
                recommendations = get_content_based_recommendations(
                    movie_title)

                recommendations = pd.DataFrame({
                    'Title': np.array(recommendations['Title']),
                    'Release_Date': np.array(recommendations['Release_Date']),
                    'Popularity': np.array(recommendations['Popularity']),
                    'Overview': np.array(recommendations['Overview']),
                    'Poster_Url': np.array(recommendations['Poster_Url'])
                })
                # print(df)
                return render_template('recomendation.html', movie_data=recommendations, index=len(recommendations), msg='found', loged=1)
            else:
                return render_template('recomendation.html', movie_data=data, index=1, msg='no', loged=1)
    except:
        return render_template('recomendation.html', movie_data=data, index=1, msg='no', loged=1)


@app.route('/movie_news')
def newsfeed():
    user_data = pd.read_csv('user_data.csv')
    if isLogedIn == 0:
        return redirect('/login')
    else:
        main_url = 'https://newsapi.org/v2/everything?q=movie&sortBy=publishedAt&apiKey=6726a5e0691b4a198f69c33d332ac2fe'
        news = []
        try:
            response = requests.get(main_url)
            news = response.json()['articles']
            print(news[0]['author'])
        except:

            pass
        return render_template('newsfeed.html', index=len(news), my_news=news, loged=isLogedIn)


@app.route('/select/movies')
def selectMovie():
    user_data = pd.read_csv('user_data.csv')
    if isLogedIn == 0:
        return redirect('/login')
    else:
        url = "http://127.0.0.1:5000/movies"

        response = requests.get(url)
        movies_to_watch = response.json()
        print(movies_to_watch)
        return render_template('select_movie.html', movie_data=movies_to_watch, index=len(movies_to_watch), msg='found', loged=isLogedIn)
        # return movies_to_watch


@app.route('/select/hall/<movieid>')
def bookHall(movieid):
    user_data = pd.read_csv('user_data.csv')
    if isLogedIn == 0:
        return redirect('/login')
    else:
        url = 'http://127.0.0.1:5000/movie_halls'
        response = requests.get(url)

        halls = response.json()['movie_halls']
        print(movieid)
        return render_template('hall.html', hall_datas=halls, mo_id=movieid, loged=isLogedIn)


@app.route('/select/seats/<name>/<mId>', methods=['POST', 'GET'])
def bookSeat(name, mId):
    my_seats = []
    url = 'http://127.0.0.1:5000/movie_halls'

    # Get the hall data from our backend API
    response = requests.get(url)
    movie_halls = response.json()['movie_halls']

    # Find the hall and extract its seats
    hall_id = None
    for hall in movie_halls:
        if hall['name'] == name:
            my_seats = hall['capacity']  # This should be a list of seat information
            hall_id = hall['id']
            break

    print("seats:")
    print(my_seats)

    if isLogedIn == 0:
        return redirect('/login')
    else:
        if request.method == 'POST':
            user_seat = request.form.get('seat')
            user_name = request.form.get('full-name')
            user_email = request.form.get('email')
            user_date = request.form.get('date')
            user_time = request.form.get('time')
            user_movie = mId

            # Find the selected seat and check its availability
            selected_seat = next((seat for seat in range(my_seats) if seat == int(user_seat)), None)
            print(selected_seat)
            # # Update the seat status to booked (status 2)
            # selected_seat['status'] = 2

            # Prepare the booking data
            booking_data = {
                'user_id': user_my_id,
                'movie_id': user_movie,
                'hall_id': hall_id,
                'seats': 1,
                'booking_date': user_date
            }

            # Make the POST request to our booking API
            booking_url = 'http://127.0.0.1:5000/book_seat'
            booking_response = requests.post(booking_url, json=booking_data)

            if booking_response.status_code == 200:
                return '<p>Booking successful. Please be on time.</p>'
            else:
                # Revert the seat status to available (status 1) if booking fails
                # selected_seat['status'] = 1
                return '<p>Booking failed. Please try again.</p>'
        return render_template('seats.html', hall_seats=my_seats, hall_name=name, movieid=mId, loged=isLogedIn)

    return '<p>Failed to retrieve seat information.</p>'


@app.route('/about')
def about():
    user_data = pd.read_csv('user_data.csv')
    if isLogedIn == 0:
        return render_template('about.html', loged=isLogedIn)
    else:
        return render_template('about.html', loged=isLogedIn)


@app.route('/addmovies', methods=['GET', 'POST'])
def addmovies():
    if request.method == "POST":
        movie_name = request.form.get('name')
        movie_genre = request.form.get('genre')
        movie_id = str(uuid.uuid4())
        movie_rating = request.form.get('rating')
        movie_r_date = request.form.get('date')
        print(movie_id)
        url = 'http://127.0.0.1:5000/movie_requests'

        body = {
            "name": movie_name,
            "genre": movie_genre,
            "rating": movie_rating,
            "release_date": movie_r_date
        }

        response = requests.post(url, json=body)
        movies = response.json()
        print(movies)
        return redirect('/movies')

    return render_template('addmovies.html', loged=isLogedIn)


@app.route('/movies/<movieId>', methods=['GET', 'POST'])
def detailmovie(movieId):
    user_data = pd.read_csv('user_data.csv')
    idofuser = user_data['user_id'][0]
    moviedata = {}
    url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies'
    response = requests.get(url)
    movies = response.json()['movies']
    print(movieId)
    for movie in movies:
        if (int(movieId)) == movie['id']:
            moviedata = movie
            print(f"the movie: {movie}")
    if request.method == "POST":
        movie_id = str(uuid.uuid4())
        movie_rating = request.form.get('rating')
        user_id = idofuser
        print(movie_rating)
        url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/ratings'

        body = {
            "rating": {
            "userId": int(user_id),
            "movieId": int(movie['id']),
            "rating": str(movie_rating)
            }
        }

        response = requests.post(url,json=body)
        rate = response.json()
        print(rate)
        return "The rating is added"
    print(moviedata)
    return render_template('detailmovie.html', mdata=moviedata, loged=isLogedIn, userid=idofuser)


@app.route('/profile')
def profile():
    print(user_my_id)
    response = requests.get(url=f'http://127.0.0.1:5000/user/{user_my_id}')
    return render_template('profile.html', loged=isLogedIn, profile= response.json())

if __name__ == '__main__':
    app.run(debug=True,port=9000)
