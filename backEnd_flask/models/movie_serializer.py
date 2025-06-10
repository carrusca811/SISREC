def movie_serializer(movie):
    return {
        "id": str(movie["_id"]),
        "title": movie.get("title"),
        "year": movie.get("year"),
        "certificate": movie.get("certificate"),
        "runtime": movie.get("runtime"),
        "genres": movie.get("genres", []),
        "imdb_rating": movie.get("imdb_rating"),
        "meta_score": movie.get("meta_score"),
        "director": movie.get("director"),
        "cast": movie.get("cast", []),
        "votes": movie.get("votes"),
        "gross": movie.get("gross"),
        "image_url": movie.get("image_url"),
         "users_review": movie.get("users_review", 0.0)
    }
