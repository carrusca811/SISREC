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
/*   trendingMoviesResults?: Movie[] = [];
  discoverMoviesResults?: Movie[] = [];
  actionMovieResults?: Movie[] = [];
  adventureMovieResults?: Movie[] = [];
  animationMovieResults?: Movie[] = [];
  comedyMovieResults?: Movie[] = [];
  documentaryMovieResults?: Movie[] = [];
  sciencefictionMovieResults?: Movie[] = [];
  thrillerMovieResults?: Movie[] = []; */
  nonPersonalizedMovies: { genre: string; top_movies: Movie[] }[] = [];
  contentBasedMovies: { genre: string; top_movies: Movie[] }[] = [];
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

    if (this.user && this.user.email.length > 0) {
        this.genres = this.user.preference_genre || [];
        this.actors = this.user.preference_actor || [];
        this.getContentBasedOnPreferences(this.genres, this.actors, 1000);
    } else {
      this.loadNonPersonalizedRecommendations();
    }
  }

  
  loadNonPersonalizedRecommendations() {
    this.moviesService.getNonPersonalizedRecommendations().subscribe({
      next: (result) => {
        this.nonPersonalizedMovies = result;
        console.log('Non-personalized recommendations:', this.nonPersonalizedMovies);
      },
      error: (err) => {
        console.error('Error loading recommendations:', err);
      }
    });
  }

  getContentBasedOnPreferences(genres: string[], actors: string[], limit: number): void {
    this.moviesService.getColdStartRecommendations(genres, actors, limit).subscribe({
      next: (result) => {
        this.contentBasedMovies = this.groupContentBasedMoviesByGenre(result);
        console.log('Grouped content-based movies:', this.contentBasedMovies);
      },
      error: (err) => {
        console.error('Error fetching content based on preferences:', err);
      }
    });
  }
  

  groupContentBasedMoviesByGenre(movies: Movie[]): { genre: string; top_movies: Movie[] }[] {
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
      top_movies: movies.slice(0, 10) // ou top_n vindo do backend
    }));
  }
 
  getEncodedImagePath(title: string): string {
    return 'assets/movies/' + encodeURIComponent(title) + '.jpg';
  }
  
}



  /* ngOnInit (): void {
    this.trendingMovies();
    this.discoverMovies();
    this.actionMovies();
    this.adventureMovies();
    this.comedyMovies();
    this.animationMovies();
    this.documentaryMovies();
    this.sciencefictionMovies();
    this.thrillerMovies();
  }

  trendingMovies () {
    this.moviesService.getTrendingMovies().subscribe((result) => {
      console.log(result, 'trendingresult#');
      this.trendingMoviesResults = result.results;
    });
  }

  discoverMovies () {
    this.moviesService.getDiscoverMovies().subscribe((result) => {
      console.log(result, 'discoverresult#');
      this.discoverMoviesResults = result.results;
    });
  }

  actionMovies () {
    this.moviesService.getActionMovies().subscribe((result) => {
      this.actionMovieResults = result.results;
    });
  }

  adventureMovies () {
    this.moviesService.getAdventureMovies().subscribe((result) => {
      this.adventureMovieResults = result.results;
    });
  }

  animationMovies () {
    this.moviesService.getAnimationMovies().subscribe((result) => {
      this.animationMovieResults = result.results;
    });
  }

  comedyMovies () {
    this.moviesService.getComedyMovies().subscribe((result) => {
      this.comedyMovieResults = result.results;
    });
  }

  documentaryMovies () {
    this.moviesService.getDocumentaries().subscribe((result) => {
      this.documentaryMovieResults = result.results;
    });
  }

  sciencefictionMovies () {
    this.moviesService.getScienceFictionMovies().subscribe((result) => {
      this.sciencefictionMovieResults = result.results;
    });
  }

  thrillerMovies () {
    this.moviesService.getThrillerMovies().subscribe((result) => {
      this.thrillerMovieResults = result.results;
    });
  }
}
 */