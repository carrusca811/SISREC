export interface Movie {
  id: string;
  title: string;
  year: number;
  certificate?: string;
  runtime: number;
  genres: string[];
  imdb_rating: number;
  meta_score?: number;
  director: string;
  cast: string[];
  votes: number;
  poster: string;
  gross?: number;
  image_url: string;
  users_review: number;
}
