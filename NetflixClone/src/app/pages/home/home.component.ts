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
      console.log('personalized');
    } else {
      this.loadNonPersonalizedRecommendations();
    }
  }
  loadNonPersonalizedRecommendations() {
    this.moviesService.getNonPersonalizedRecommendations().subscribe({
      next: (result) => {
        this.nonPersonalizedMovies = result;
      },
      error: (err) => {
        console.error('Error loading recommendations:', err);
      }
    });
  }
  
  onImageError(event: Event) {
    const target = event.target as HTMLImageElement;
    target.src = 'assets/movies/default.jpg';
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
}
