# # import requests

# # data = {
# #     'rajmoniMovieHall': {
# #             "seatsName": "a1",
# #             "status": "sdvlw",
# #             "userEmail": "sldfow",
# #             "userId": "ldsnd",
# #             "movieId": "nfwl",
# #             "date": "nldf",
# #             "time": "d",
# #         }
# # }

# # # url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/rajmoniMovieHall'
# # url = 'https://api.sheety.co/e78e679bf4063c1cfa9e4f16869c45b0/movieRecomendationSystemDatabase/rajmoniMovieHall/2'

# # response = requests.put(url,json=data,headers={'Content-Type':'application/json'})

# # seats = response.json()

# # # for s in seats:
# # #     if s['seatsName'] == 'a1':
# # #         s['seatsName']
# # #         print(s['id'])
# # #     else:
# # #         continue

# # print(seats)
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import linear_kernel
# import numpy as np

# # Load the dataset
# data = pd.read_csv('mymoviedb.csv', lineterminator='\n')

# # Create TF-IDF vectorizer
# tfidf = TfidfVectorizer(stop_words='english')

# # Compute TF-IDF matrix
# tfidf_matrix = tfidf.fit_transform(data['Overview'].fillna(''))

# # Compute cosine similarity matrix
# cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# # Function to get movie recommendations based on content similarity
# def get_content_based_recommendations(title, cosine_sim=cosine_sim, data=data, top_n=5):
#     # Convert all titles and the search term to lowercase for case-insensitive and partial matching
#     data['Title_lower'] = data['Title'].str.lower()
#     title_lower = title.lower()

#     # Find titles containing the search term
#     matching_titles = data[data['Title_lower'].str.contains(title_lower, na=False)]

#     # If there are no matching titles, return an empty DataFrame
#     if matching_titles.empty:
#         return pd.DataFrame(columns=['Title', 'Release_Date', 'Popularity', 'Overview', 'Poster_Url'])

#     # Use the first matching title for recommendations (you can modify this logic based on your requirements)
#     first_matching_title = matching_titles.iloc[0]
    
#     # Get the index of the matching title
#     idx = data[data['Title_lower'] == first_matching_title['Title_lower']].index[0]
    
#     scores = list(enumerate(cosine_sim[idx]))
#     scores = sorted(scores, key=lambda x: x[1], reverse=True)
#     top_scores = scores[1:top_n+1]
#     movie_indices = [i[0] for i in top_scores]
    
#     return data[['Title', 'Release_Date', 'Popularity', 'Overview', 'Poster_Url']].iloc[movie_indices]

# # Example of how to use the model
# search_term = "spider"
# recommendations = get_content_based_recommendations(search_term)
# print(recommendations)



import requests

url = 'https://api.sheety.co/e95f9a17ccc7443f8984c47405ffaac2/movieRecomendationSystemDatabase/loginRegistration'
response = requests.get(url)

if response.status_code == 200:
    json_data = response.json()
    # Do something with the data
    print(json_data['loginRegistration'])
else:
    print(f"Failed to retrieve data: {response.status_code}")
