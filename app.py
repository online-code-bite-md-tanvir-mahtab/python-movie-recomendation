from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import requests
import uuid

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


global isLogedIn
index_count = 0


def isAuthenticated(u_pass, u_email):
    isAuth = False
    main_url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/loginRegistration'
    response = requests.get(url=main_url)
    news = response.json()['loginRegistration']
    index_count = len(news)
    for n in news:
        email = n['email']
        passw = n['password']
        userId = n['id']

        if email == u_email and passw == u_pass:
            data = {
                'email': [email],
                'user_id': [userId]
            }
            df = pd.DataFrame(data)
            df.to_csv("user_data.csv", index=False)
            isAuth = True
            isLogedIn = 1
            _isLogedIn(userId, isLogedIn)
        else:
            continue
    return isAuth


def isRegisterd(u_name, u_email, u_phone, u_password):
    urls = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/loginRegistration'
    body = {
        'loginRegistration': {
            'name': u_name,
            'email': u_email,
            'password': u_password,
            'isLogedIn': 0,
            'id': str(uuid.uuid4()),
            'phone': u_phone,
        }
    }
    response = requests.post(url=urls, json=body)
    news = response
    print(news.json())
    if news.status_code == 200:
        print("responded")
        return True
    else:
        return False


def _isLogedIn(user_id, logedinOrNot):
    body = {
        'loginRegistration': {
            'isLogedIn': logedinOrNot,
        }
    }
    main_url = f'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/loginRegistration/{user_id}'
    response = requests.put(url=main_url, json=body)
    news = response.json()
    print(news)


app = Flask(__name__)


@app.route('/')
def home():
    user_data = pd.read_csv('user_data.csv')
    if user_data.empty:
        return render_template('index.html', loged=0)
    else:
        return render_template('index.html', loged=1)


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


@app.route('/logout')
def logout():
    df = pd.read_csv('user_data.csv')
    userid = df['user_id'][0]
    _isLogedIn(userid, 0)
    df.drop(axis=0, inplace=True, index=0)
    df.to_csv('user_data.csv', index=False)
    return redirect('/login')


@app.route('/movies', methods=['GET', 'POST'])
def movies():
    url = "https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies"

    response = requests.get(url)
    movies_to_search = response.json()['movies']
    # print(movies_to_search)
    user_data = pd.read_csv('user_data.csv')
    data = pd.DataFrame(movies_to_search)
    if user_data.empty:
        return render_template('movies.html', movie_data=data, index=100, msg='found', loged=0)
    else:

        if request.method == 'POST':
            search_name = request.form.get('email')
            print(f"my value:{search_name}is")
            searched_data = data[data['name'] ==
                                 search_name].reset_index(drop=True)
            print(f"search found: {len(searched_data)}")
            if len(searched_data) == 0:
                if user_data.empty:
                    return redirect('login')
                else:
                    return render_template('movies.html', movie_data=data, index=0, msg='no', loged=1)
            else:
                return render_template('movies.html', movie_data=searched_data, index=100, msg='found', loged=1)
        else:
            return render_template('movies.html', movie_data=data, index=100, msg='found', loged=1)


@app.route('/recomend', methods=['GET', 'POST'])
def recomend():
    try:
        # Load the dataset
        data = pd.read_csv('mymoviedb.csv', lineterminator='\n')
        user_data = pd.read_csv('user_data.csv')
        if user_data.empty:
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
    if user_data.empty:
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
        return render_template('newsfeed.html', index=len(news), my_news=news, loged=1)


@app.route('/select/movies')
def selectMovie():
    user_data = pd.read_csv('user_data.csv')
    if user_data.empty:
        return redirect('/login')
    else:
        url = "https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies"

        response = requests.get(url)
        movies_to_watch = response.json()['movies']
        print(movies_to_watch)
        return render_template('select_movie.html', movie_data=movies_to_watch, index=len(movies_to_watch), msg='found', loged=1)
        # return movies_to_watch


@app.route('/select/hall/<movieid>')
def bookHall(movieid):
    user_data = pd.read_csv('user_data.csv')
    if user_data.empty:
        return redirect('/login')
    else:
        url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/tikets'
        response = requests.get(url)

        halls = response.json()['tikets']
        print(movieid)
        return render_template('hall.html', hall_datas=halls, mo_id=movieid, loged=1)


@app.route('/select/seats/<name> <mId>', methods=['POST', 'GET'])
def bookSeat(name, mId):
    my_seats = []
    url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/rajmoniMovieHall'

    response = requests.get(url)

    seats = response.json()['rajmoniMovieHall']
    user_data = pd.read_csv('user_data.csv')
    my_seats = [seat['seatsName'] for seat in seats]
    print(my_seats)
    if user_data.empty:
        return redirect('/login')
    else:
        if request.method == 'POST':
            user_seat = request.form.get('seat')
            user_name = request.form.get('full-name')
            user_email = request.form.get('email')
            user_date = request.form.get('date')
            user_time = request.form.get('time')
            user_movie = mId

            print(seats)
            for s in seats:
                if s['seatsName'] == user_seat:
                    my_seats.append(s['seatsName'])
                    data = {
                        'rajmoniMovieHall': {
                            "seatsName": user_seat,
                            "status": 2,
                            "userEmail": user_email,
                            "userId": 0,
                            "movieId": mId,
                            "date": user_date,
                            "time": user_time,
                        }
                    }
                    url = f'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/rajmoniMovieHall/{s["id"]}'
                    response = requests.put(url, json=data, headers={
                                            'Content-Type': 'application/json'})
                    seats = response.json()
                    return '<p>Please Be On Time</p>'
                else:
                    continue

            return '<p>Please Be On Time</p>'
        return render_template('seats.html', hall_seats=my_seats, hall_name=name, movieid=mId, loged=1)


@app.route('/about')
def about():
    user_data = pd.read_csv('user_data.csv')
    if user_data.empty:
        return render_template('about.html', loged=0)
    else:
        return render_template('about.html', loged=1)


@app.route('/addmovies', methods=['GET', 'POST'])
def addmovies():
    if request.method == "POST":
        movie_name = request.form.get('name')
        movie_genre = request.form.get('genre')
        movie_id = str(uuid.uuid4())
        movie_rating = request.form.get('rating')
        movie_r_date = request.form.get('date')
        print(movie_id)
        url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies'

        body = {
            'movie': {
                "id": movie_id,
                "name": movie_name,
                "genre": movie_genre,
                "rating": movie_rating,
                "releaseDate": movie_r_date,
            }
        }

        response = requests.post(url, json=body)
        movies = response.json()
        print(movies)
        return redirect('/movies')

    return render_template('addmovies.html', loged=1)


@app.route('/movies/<movieId>', methods=['GET', 'POST'])
def detailmovie(movieId):
    moviedata = {}
    url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies'
    response = requests.get(url)
    movies = response.json()['movies']
    print(movieId)
    for movie in movies:
        if (int(movieId)-1) == movie['id']:
            moviedata = movie
            print(f"the movie: {movie}")
    if request.method == "POST":
        movie_name = request.form.get('name')
        movie_genre = request.form.get('genre')
        movie_id = str(uuid.uuid4())
        movie_rating = request.form.get('rating')
        movie_r_date = request.form.get('date')
        print(movie_id)
        url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/movies'

        # body = {
        #     'movie': {
        #         "id": movie_id,
        #         "name": movie_name,
        #         "genre": movie_genre,
        #         "rating": movie_rating,
        #         "releaseDate": movie_r_date,
        #     }
        # }

        response = requests.get(url)
        movie = response.json()
        return "The rating is added"
    print(moviedata)
    return render_template('detailmovie.html', mdata=moviedata, loged=1)


if __name__ == '__main__':
    app.run(debug=True)
