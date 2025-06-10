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
  contentBasedRecommendations: any;
  collaborativeMovies: any;

  groupedColdStart: { genre: string; slides: Movie[][] }[] = [];
  groupedNonPersonalized: { genre: string; slides: Movie[][] }[] = [];
  groupedContentBased: { genre: string; slides: Movie[][] }[] = [];
  groupedCollaborative: { genre: string; slides: Movie[][] }[] = [];
  groupedHybrid: { genre: string; slides: Movie[][] }[] = [];

  genres: string[] = [];
  actors: string[] = [];
  user: any;
  localUser: any;

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


  orderGroupsByPreferences(groups: { genre: string; slides: Movie[][] }[], preferences: string[]): { genre: string; slides: Movie[][] }[] {
    return groups.sort((a, b) => {
      const indexA = preferences.indexOf(a.genre);
      const indexB = preferences.indexOf(b.genre);
  
      if (indexA === -1 && indexB === -1) return 0; 
      if (indexA === -1) return 1; 
      if (indexB === -1) return -1; 
      return indexA - indexB;
    });
  }
  

  verActiveUser(): void {
    this.localUser = this.storageService.getItem('user');
    const userId = this.localUser?.id || this.localUser?._id;
  
    if (!userId) {
      this.loadNonPersonalizedRecommendations();
      return;
    }
  
    this.userService.getUserById(userId).subscribe({
      next: (user) => {
        this.user = user;
        this.storageService.setItem('user', user);
  
        const numReviews = user?.numReviews || 0;
        console.log('Número de avaliações do utilizador:', numReviews);
  
        if (numReviews < 5) {
          this.genres = user.preference_genre || [];
          this.actors = user.preference_actor || [];
          this.getColdStartPreferences(this.genres, this.actors, 1000);
        } else if (numReviews < 30) {
          this.getContentBasedRecommendationsForUser();
        } else {
          this.getHybridRecommendations();
        }
      },
      error: (err) => {
        console.error('Erro ao obter utilizador do backend:', err);
        this.loadNonPersonalizedRecommendations();
      },
    });
  }
  
  

  getHybridRecommendations(): void {
    this.moviesService.getHybridRecommendations(this.user?.id).subscribe({
      next: (result) => {
        console.log('Recomendações Híbridas:', result);
        this.groupedHybrid = this.orderGroupsByPreferences(
          result.map(group => ({
            genre: group.genre,
            slides: this.chunk(group.top_movies, 5)
          })),
          this.user?.preference_genre || []
        );
        
      },
      error: (err) => {
        console.error('Erro nas recomendações híbridas:', err);
      }
    });
  }

  

  getCollaborativeRecommendations(userId: string): void {
    this.moviesService.getCollaborativeRecommendations(userId).subscribe({
      next: (movies: Movie[]) => {
        console.log("🤝 Collaborative Recommendations:", movies);
        this.groupedCollaborative = this.groupMoviesByGenre(movies);
      },
      error: (err) => {
        console.error("Erro ao obter recomendações colaborativas:", err);
      }
    });
    
  }
  
  

  getContentBasedRecommendationsForUser(): void {
    this.moviesService.getContentBasedRecommendations(this.user?.id).subscribe({
      next: (result) => {
        this.contentBasedRecommendations = result;
        this.groupedContentBased = this.orderGroupsByPreferences(
          result.map(group => ({
            genre: group.genre,
            slides: this.chunk(group.top_movies, 5)
          })),
          this.user?.preference_genre || []
        );
        
        console.log('📊 Content-Based Recommendations:', result);
      },
      error: (err) => {
        console.error('❌ Erro nas recomendações content-based:', err);
      },
    });
  }

  loadNonPersonalizedRecommendations(): void {
    this.moviesService.getNonPersonalizedRecommendations().subscribe({
      next: (result) => {
        this.nonPersonalizedMovies = result;
        this.groupedNonPersonalized = result.map((group: { genre: string; top_movies: Movie[] }) => ({
          genre: group.genre,
          slides: this.chunk(group.top_movies, 5),
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
        this.groupedColdStart = this.orderGroupsByPreferences(
          this.groupMoviesByGenre(result),
          this.user?.preference_genre || []
        );
        
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

    const grouped = Array.from(genreMap.entries()).map(([genre, movies]) => ({
      genre,
      slides: this.chunk(movies, 6),
    }));

    console.log('Grouped Movies by Genre:', grouped);
    return grouped;
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
