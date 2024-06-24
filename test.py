import csv
import requests
from datetime import datetime

def insert_movies_from_csv(csv_file_path, api_url):
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            movies_added = 0
            for row in reader:
                try:
                    # Convert string date to datetime object
                    release_date = datetime.strptime(row['Release_Date'], '%Y-%m-%d').date()

                    title = row['Title']
                    overview = row['Overview']
                    popularity = float(row['Popularity']) if row['Popularity'] else None
                    vote_count = int(row['Vote_Count']) if row['Vote_Count'] else None
                    vote_average = float(row['Vote_Average']) if row['Vote_Average'] else None
                    original_language = row['Original_Language']
                    genre = row['Genre']
                    poster_url = row['Poster_Url']

                    # Prepare the movie data
                    print(release_date.strftime('%Y-%m-%d')+"hello")
                    movie_data = {
                        'Release_Date': release_date.strftime('%Y-%m-%d'),  # Convert datetime to string
                        'Title': title,
                        'Overview': overview,
                        'Popularity': popularity,
                        'Vote_Count': vote_count,
                        'Vote_Average': vote_average,
                        'Original_Language': original_language,
                        'Genre': genre,
                        'Poster_Url': poster_url
                    }

                    # Make the POST request to the add movie API
                    response = requests.post(api_url, json=movie_data)
                    
                    if response.status_code == 201:
                        movies_added += 1
                    else:
                        print(f"Failed to add movie {title}: {response.status_code} {response.text}")
                except Exception as e:
                    print(f"Error processing movie {row.get('Title', 'Unknown')}: {e}")
            print(f"Successfully added {movies_added} movies to the database via API.")
    except Exception as e:
        print(f"Failed to read the CSV file: {e}")

# Example usage
# insert_movies_from_csv('path_to_your_file.csv', 'http://127.0.0.1:5000/movies')


# Example usage
insert_movies_from_csv('mymoviedb.csv', 'http://127.0.0.1:5000/add_movie')
