import { Component, OnInit } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { Router } from '@angular/router';
import { Movie } from 'src/app/components/model/movie.model';
import { AppStorageService } from 'src/app/services/app.storage.service';
import { MoviesService } from 'src/app/services/movies.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: false,
})
export class HomeComponent implements OnInit {
  nonPersonalizedMovies: { genre: string; top_movies: Movie[] }[] = [];
  coldStartMovies: { genre: string; top_movies: Movie[] }[] = [];

  groupedColdStart: { genre: string; slides: Movie[][] }[] = [];
  groupedNonPersonalized: { genre: string; slides: Movie[][] }[] = [];

  genres: string[] = [];
  actors: string[] = [];
  user: any;

  constructor(
    private moviesService: MoviesService,
    private userService: UserService,
    private title: Title,
    private meta: Meta,
    private router: Router,
    private storageService: AppStorageService
  ) {}

  ngOnInit(): void {
    this.verActiveUser();
  }

  verActiveUser(): void {
    this.user = this.storageService.getItem('user');

    if (this.user && this.user.email?.length > 0) {
      const numReviews = this.user?.number_of_reviews || 0;

      if (numReviews < 3) {
        this.genres = this.user.preference_genre || [];
        this.actors = this.user.preference_actor || [];
        this.getColdStartPreferences(this.genres, this.actors, 1000);
      } else {
        this.loadNonPersonalizedRecommendations();
      }
    }
  }

  loadNonPersonalizedRecommendations() {
    this.moviesService.getNonPersonalizedRecommendations().subscribe({
      next: (result) => {
        this.nonPersonalizedMovies = result;
        this.groupedNonPersonalized = result.map((group: { genre: any; top_movies: Movie[]; }) => ({
          genre: group.genre,
          slides: this.chunk(group.top_movies, 6)
        }));
      },
      error: (err) => {
        console.error('Error loading recommendations:', err);
      },
    });
  }

  getColdStartPreferences(genres: string[], actors: string[], limit: number): void {
    this.moviesService.getColdStartRecommendations(genres, actors, limit).subscribe({
      next: (result) => {
        console.log('Cold Start Recommendations:', result);
        this.groupedColdStart = this.groupMoviesByGenre(result);
      },
      error: (err) => {
        console.error('Error fetching content based on preferences:', err);
      },
    });
  }

  groupMoviesByGenre(movies: Movie[]): { genre: string; slides: Movie[][] }[] {
    const genreMap = new Map<string, Movie[]>();

    for (const movie of movies) {
      if (movie.genres) {
        for (const genre of movie.genres) {
          const list = genreMap.get(genre) || [];
          list.push(movie);
          genreMap.set(genre, list);
        }
      }
    }

    return Array.from(genreMap.entries()).map(([genre, movies]) => ({
      genre,
      slides: this.chunk(movies, 6)
    }));

    console.log('Grouped Movies by Genre:', this.groupedColdStart);
  }

  chunk(array: Movie[], size: number): Movie[][] {
    const result: Movie[][] = [];
    for (let i = 0; i < array.length; i += size) {
      result.push(array.slice(i, i + size));
    }
    return result;
  }

  getEncodedImagePath(title: string): string {
    return 'assets/movies/' + encodeURIComponent(title) + '.jpg';
  }
}
