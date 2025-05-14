import random
from database import users_collection, movies_collection
from bson import ObjectId

def get_popular_movies(limit=10):
    """
    Get the most popular movies based on ratings.
    """
    try:
        movies = list(movies_collection.find().sort("imdb_rating", -1).limit(limit))
        return movies
    except Exception as e:
        print(f"Error retrieving popular movies: {str(e)}")
        return []

def recommend_based_on_preferences(user):
    """
    Recommend movies based on user preferences (genre and actor).
    """
    try:
        query = {}
        if user.get("preference_genre"):
            query["genres"] = {"$in": user["preference_genre"]}
        if user.get("preference_actor"):
            query["cast"] = {"$in": user["preference_actor"]}
        
        recommended_movies = list(movies_collection.find(query).limit(10))
        
        # Fallback to popular movies if no match
        if not recommended_movies:
            recommended_movies = get_popular_movies()

        return recommended_movies
    except Exception as e:
        print(f"Error recommending movies: {str(e)}")
        return []

def cold_start_user(user_id):
    """
    Handle cold start problem for a new user.
    """
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            print(f"User with ID {user_id} not found.")
            return get_popular_movies()

        if user.get("preference_genre") or user.get("preference_actor"):
            return recommend_based_on_preferences(user)
        else:
            return get_popular_movies()

    except Exception as e:
        print(f"Error in cold start for user: {str(e)}")
        return get_popular_movies()

def cold_start_item(movie_id):
    """
    Handle cold start for a new movie (recommend similar movies).
    """
    try:
        movie = movies_collection.find_one({"_id": ObjectId(movie_id)})
        
        if not movie:
            print(f"Movie with ID {movie_id} not found.")
            return get_popular_movies()

        # Use genres and cast to find similar movies
        query = {
            "genres": {"$in": movie.get("genres", [])},
            "cast": {"$in": movie.get("cast", [])}
        }
        
        similar_movies = list(movies_collection.find(query).limit(10))
        
        # Fallback to popular movies if no similar movies found
        if not similar_movies:
            similar_movies = get_popular_movies()

        return similar_movies

    except Exception as e:
        print(f"Error in cold start for item: {str(e)}")
        return get_popular_movies()
