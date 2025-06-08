import { Component, OnInit } from "@angular/core";
import { FormControl, FormGroup } from "@angular/forms";
import { Meta, Title } from "@angular/platform-browser";
import { MoviesService } from "src/app/services/movies.service";


@Component({
    selector: 'app-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.scss'],
    standalone: false
})
export class SearchComponent implements OnInit {

  constructor (private moviesService: MoviesService, private title: Title, private meta: Meta) {}

  ngOnInit (): void {
  }

  searchResult: any;
  searchForm = new FormGroup({
    'movieName': new FormControl('')
  });

  onSubmit() {
    const movieName = (this.searchForm.value.movieName)?.trim();
    if (!movieName) {
      return; // ignora pesquisa vazia
    }
  
    this.moviesService.getMoviesByName(movieName).subscribe({
      next: (result) => {
        console.log(result, 'searchResults##');
        this.searchResult = result;
      },
      error: (err) => {
        console.error('Error fetching movies:', err);
      },
      complete: () => {
        this.searchForm.reset();
      }
    });
  }
  
  
}
