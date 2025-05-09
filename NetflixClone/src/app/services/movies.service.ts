import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Movie } from '../components/model/movie.model';

@Injectable({
  providedIn: 'root'
})
export class MoviesService {

  private baseURL = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

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

  /** Get Movie Cast - Simulating as part of the movie object */
  getMovieCast(id: string): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseURL}/movies/${id}/cast`);
  }

  /** Get Movie Video - Simulating as part of the movie object */
  getMovieVideo(id: string): Observable<string> {
    return this.http.get<string>(`${this.baseURL}/movies/${id}/video`);
  }
}
