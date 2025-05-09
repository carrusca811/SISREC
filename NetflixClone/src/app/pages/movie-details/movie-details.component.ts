import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MoviesService } from '../../services/movies.service';
import { Movie } from 'src/app/components/model/movie.model';

@Component({
  selector: 'app-movie-details',
  templateUrl: './movie-details.component.html',
  styleUrls: ['./movie-details.component.scss']
})
export class MovieDetailsComponent implements OnInit {

  movie: Movie | null = null;
  cast: string[] = [];
  videoUrl: string = '';
  errorMessage: string = '';

  constructor(
    private moviesService: MoviesService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const movieId = this.route.snapshot.paramMap.get('id');
    if (movieId) {
      this.getMovieDetails(movieId);
    }
  }

  getMovieDetails(id: string): void {
    this.moviesService.getMovieDetails(id).subscribe({
      next: (data) => {
        this.movie = data;
      },
      error: (err) => {
        this.errorMessage = 'Error fetching movie details';
        console.error(err);
      }
    });

    this.moviesService.getMovieCast(id).subscribe({
      next: (data) => {
        this.cast = data;
      },
      error: (err) => {
        console.error('Error fetching cast:', err);
      }
    });

    this.moviesService.getMovieVideo(id).subscribe({
      next: (data) => {
        this.videoUrl = data;
      },
      error: (err) => {
        console.error('Error fetching video:', err);
      }
    });
  }
}
