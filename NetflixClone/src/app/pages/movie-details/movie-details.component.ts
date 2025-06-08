import { Component, OnInit } from '@angular/core';
import { MoviesService } from '../../services/movies.service';
import { Movie } from 'src/app/components/model/movie.model';
import { User } from 'src/app/components/model/user.model';
import { ActivatedRoute } from '@angular/router';
import { AppStorageService } from 'src/app/services/app.storage.service';

@Component({
  selector: 'app-movie-details',
  templateUrl: './movie-details.component.html',
  styleUrls: ['./movie-details.component.scss'],
  standalone: false,
})
export class MovieDetailsComponent implements OnInit {
  movie: Movie | null = null;
  rating: number = 0;
  cast: string[] = [];
  videoUrl: string = '';
  errorMessage: string = '';

  constructor(
    private moviesService: MoviesService,
    private route: ActivatedRoute,
        private storageService: AppStorageService // Assuming you have a StorageService for user data
  ) {}

  ngOnInit(): void {
    const movieId = this.route.snapshot.paramMap.get('id');
    this.getMovieDetails(movieId || '');
  }

  getMovieDetails(id: string): void {
    this.moviesService.getMovieDetails(id).subscribe({
      next: (data) => {
        this.movie = data;
        this.videoUrl = 'https://www.youtube.com/results?search_query=' + encodeURIComponent(this.movie?.title + ' trailer');
        console.log('Movie Details:', this.movie);
      },
      error: (err) => {
        this.errorMessage = 'Error fetching movie details';
        console.error(err);
      },
    });
  }

  onRatingSet(rating: number): void {
    console.warn(`User set rating to ${rating}`);
    this.rating = rating;
  }

  submitReview(): void {
    const user = this.storageService.getItem('user') as User;    
    if (!this.movie || !user?.id) return;

    const payload = {
      user_id: user.id,
      movie_id: this.movie.id,
      rating: this.rating,
    };

    console.log('Submitting review:', payload);

/*     this.moviesService.submitReview(payload).subscribe({
      next: () => {
        alert('Avaliação submetida com sucesso!');
        this.rating = 0;
      },
      error: (err) => {
        console.error(err);
        alert('Erro ao submeter a avaliação.');
      },
    }); */
  }
}
