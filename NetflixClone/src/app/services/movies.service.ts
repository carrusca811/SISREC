import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Movie } from '../components/model/movie.model';

@Injectable({
  providedIn: 'root',
})
export class MoviesService {
  private baseURL = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getNonPersonalizedRecommendations(): Observable<any> {
    return this.http.get<any>(
      `${this.baseURL}/movies/non_personalized_recommendations`
    );
  }

  getColdStartRecommendations(
    genres: string[],
    actors: string[],
    topN: number = 100
  ) {
    const params = {
      genres: genres,
      actors: actors,
      top_n: topN.toString(),
    };

    return this.http.get<any[]>(
      `${this.baseURL}/movies/cold_start_recommendations`,
      { params }
    );
  }

  /** Fetch All Movies */
  getAllMovies(): Observable<Movie[]> {
    return this.http.get<Movie[]>(`${this.baseURL}/movies`);
  }

  /** Fetch Movies by Genre */
  getMoviesByGenre(genre: string): Observable<Movie[]> {
    return this.http.get<Movie[]>(`${this.baseURL}/movies?genre=${genre}`);
  }

  /** Fetch Movie Details by ID */
  getMovieDetails(id: string): Observable<Movie> {
    return this.http.get<Movie>(`${this.baseURL}/movies/${id}`);
  }

  /** Fetch Trending Movies (Dummy) */
  getTrendingMovies(): Observable<Movie[]> {
    // Assuming that trending movies are just a filter by rating
    return this.http.get<Movie[]>(`${this.baseURL}/movies?min_rating=8`);
  }

  /** Search Movies by Title */
  searchMovies(title: string): Observable<Movie[]> {
    return this.http.get<Movie[]>(`${this.baseURL}/movies?title=${title}`);
  }
  /* 
  getMovieCast(id: string): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseURL}/movies/${id}/cast`);
  }

  getMovieVideo(id: string): Observable<string> {
    return this.http.get<string>(`${this.baseURL}/movies/${id}/video`);
  } */

  getMoviesByName(name: string) {
    return this.http.get<any[]>(
      `http://localhost:8000/movies/search?name=${encodeURIComponent(name)}`
    );
  }


  makeReview(payload: any): Observable<any> {
    return this.http.post<any>(
      `${this.baseURL}/movies/review`,
      payload
    );
  }
}
