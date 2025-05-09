export interface Movie {
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
    gross?: number;
  }