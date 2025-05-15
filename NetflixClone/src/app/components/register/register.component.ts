import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { UserService } from 'src/app/services/user.service';

interface Option {
  label: string;
  value: string;
}

@Component({
    selector: 'app-register',
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.scss'],
    standalone: false
})
export class RegisterComponent implements OnInit {

  formRegister: FormGroup;
  registerError: string | null = null;
  isSelectingPreferences: boolean = false;
  selectedGenres: string[] = [];
  selectedActors: string[] = [];
  showGenreDropdown: boolean = false;
  showActorDropdown: boolean = false;
  genreSearchQuery: string = '';
actorSearchQuery: string = '';
filteredGenres: Option[] = [];
filteredActors: Option[] = [];

  availableGenres: string[] = ["Drama","Comedy","Crime","Action","Thriller","Romance","Biography","Mystery","Animation"];
  availableActors: string[] =  [
    "Tim Robbins", "Marlon Brando", "Christian Bale", "Al Pacino", "Henry Fonda",
    "Elijah Wood", "John Travolta", "Liam Neeson", "Leonardo DiCaprio", "Brad Pitt",
    "Tom Hanks", "Clint Eastwood", "Lilly Wachowski", "Robert De Niro", "Mark Hamill",
    "Jack Nicholson", "Lin-Manuel Miranda", "Kang-ho Song", "Suriya", "Matthew McConaughey",
    "Kátia Lund", "Daveigh Chase", "Roberto Benigni", "Morgan Freeman", "Jodie Foster",
    "Tatsuya Nakadai", "Toshirô Mifune", "James Stewart", "Joaquin Phoenix", "Miles Teller",
    "Éric Toledano", "Adrien Brody", "Russell Crowe", "Edward Norton", "Kevin Spacey",
    "Jean Reno", "Rob Minkoff", "Arnold Schwarzenegger", "Philippe Noiret", "Tsutomu Tatsumi",
    "Michael J. Fox", "Anthony Perkins", "Humphrey Bogart", "Charles Chaplin", "Zain Al Rafeea",
    "Erdem Can", "Pushkar", "Ryûnosuke Kamiki", "Aamir Khan", "Peter Ramsey",
    "Joe Russo", "Adrian Molina", "Jamie Foxx", "Amole Gupte", "Ben Burtt",
    "Ulrich Mühe", "Choi Min-sik", "Guy Pearce", "Yôji Matsuda", "Harrison Ford",
    "Martin Sheen", "Sigourney Weaver", "Rajesh Khanna", "Peter Sellers", "Tyrone Power",
    "Kirk Douglas", "William Holden", "Dean-Charles Chapman", "Anand Gandhi", "Ayushmann Khurrana",
    "Mohanlal", "Mads Mikkelsen", "Payman Maadi", "Lubna Azabal", "Aras Bulut Iynemli",
    "Çetin Tekindor", "Jim Carrey", "Audrey Tautou", "Jason Statham", "Ellen Burstyn",
    "Robin Williams", "Mohammad Amir Naji", "Mel Gibson", "Harvey Keitel", "Matthew Modine",
    "Aleksey Kravchenko", "F. Murray Abraham", "Paul Newman", "Malcolm McDowell", "Keir Dullea",
    "Peter O'Toole", "Jack Lemmon", "Cary Grant", "Gene Kelly", "Takashi Shimura",
    "Lamberto Maggiorani", "Fred MacMurray", "Peter Lorre", "Brigitte Helm", "Sushant Singh Rajput",
    "Vicky Kaushal", "Yash", "Viggo Mortensen", "Frances McDormand", "Irrfan Khan",
    "Prabhas", "Carlos Martínez López", "Ajay Devgn", "Kangana Ranaut", "Lembit Ulfsak",
    "Farhan Akhtar", "Manoj Bajpayee", "Rajat Barmecha", "Ricardo Darín", "Tom Hardy",
    "Bob Peterson", "Shah Rukh Khan", "Daniel Day-Lewis", "Ivana Baquero", "Hugo Weaving",
    "Amitabh Bachchan", "Bruno Ganz", "Chieko Baishô", "Akshay Kumar", "Jason Flemyng",
    "Sener Sen", "Davor Dujmovic", "Hitoshi Takagi", "Bruce Willis", "Alisa Freyndlikh",
    "Ingrid Bergman", "Anthony Quinn", "Sanjeev Kumar", "Terry Jones", "Steve McQueen",
    "Gregory Peck", "Spencer Tracy", "Marilyn Monroe", "Victor Sjöström", "Max von Sydow",
    "Jean Servais", "Ray Milland", "Chishû Ryû", "Bette Davis", "Carole Lombard",
    "Buster Keaton", "Noémie Merlant", "Taapsee Pannu", "Miyu Irino", "Mario Casas",
    "Kim Min-hee", "Anne Dorval", "Shahid Kapoor", "Hugh Jackman", "Brie Larson",
    "Darío Grandinetti", "Kemp Powers", "Haluk Bilginer", "Paresh Rawal", "Ralph Fiennes",
    "Ben Affleck", "Aoi Miyazaki", "Andrew Garfield", "Ronnie Del Carmen", "Ranbir Kapoor",
    "Chiwetel Ejiofor", "Daniel Brühl", "Matt Damon", "Mark Ruffalo", "David Rawle",
    "Vidya Balan", "Hrithik Roshan", "Anupam Kher", "Daniel Radcliffe", "Masahiro Motoki",
    "Richard Gere", "Toni Collette", "Chris Sanders", "Emile Hirsch", "Joel Coen",
    "Sanjay Dutt", "Hilary Swank", "Don Cheadle", "Jang Dong-Gun", "Ethan Hawke",
    "Uma Thurman", "Lee Unkrich", "Emilio Echevarría", "David Silverman", "Kazuya Tsurumaki",
    "Tim Roth", "Bajram Severdzan", "Ethan Coen", "Tony Chiu-Wai Leung", "Ewan McGregor",
    "Predrag 'Miki' Manojlovic", "Vincent Cassel", "Irène Jacob", "Brigitte Lin", "Sam Neill",
    "Leslie Cheung", "Gong Li", "Wil Wheaton", "Charlie Sheen", "Harry Dean Stanton"
  ];
  genreOptions: Option[] = [];
  actorOptions: Option[] = [];

  constructor(private service: UserService, private router: Router) {
    this.formRegister = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [Validators.required, Validators.minLength(6)]),
    });
  }

  ngOnInit(): void {
      this.genreOptions = this.availableGenres.map(genre => ({ label: genre, value: genre }));
      this.actorOptions = this.availableActors.map(actor => ({ label: actor, value: actor }));
    
      this.filteredGenres = this.genreOptions;
      this.filteredActors = this.actorOptions;
    }
    
    filterOptions(type: 'genre' | 'actor'): void {
      const query = type === 'genre' ? this.genreSearchQuery.toLowerCase() : this.actorSearchQuery.toLowerCase();
      const options = type === 'genre' ? this.genreOptions : this.actorOptions;
    
      const filtered = options.filter(option =>
        option.label.toLowerCase().includes(query)
      );
    
      if (type === 'genre') {
        this.filteredGenres = filtered;
      } else {
        this.filteredActors = filtered;
      }
    }
  

  onSubmit(): void {
    if (this.formRegister.valid) {
      const { email, password } = this.formRegister.value;

      const user = {
        email,
        password,
        preference_genre: [],
        preference_actor: []
      };

      this.service.register(user)
        .then(response => {
          this.registerError = null;
          const userId = response.id;
          sessionStorage.setItem('user_id', userId);
          this.isSelectingPreferences = true;
        })
        .catch(err => {
          this.registerError = err.message || 'Error during registration.';
        });
    } else {
      this.registerError = 'Please fill out all fields correctly.';
    }
  }

  savePreferences(): void {
    const userId = sessionStorage.getItem('user_id');

    if (!userId) {
      this.registerError = 'User ID not found.';
      return;
    }

    if (this.selectedGenres.length !== 2 || this.selectedActors.length !== 2) {
      this.registerError = 'Select exactly 2 genres and 2 actors.';
      return;
    }

    const preferences = {
      user_id: userId,
      preference_genre: this.selectedGenres,
      preference_actor: this.selectedActors,
    };

    this.service.updatePreferences(preferences)
      .then(() => {
        sessionStorage.removeItem('user_id');
        this.isSelectingPreferences = false;
        this.router.navigate(['/login']);
      })
      .catch(err => {
        this.registerError = err.message || 'Error updating preferences.';
      });
  }



  
toggleDropdown(type: 'genre' | 'actor'): void {
  if (type === 'genre') {
    this.showGenreDropdown = !this.showGenreDropdown;
    this.showActorDropdown = false;
  } else {
    this.showActorDropdown = !this.showActorDropdown;
    this.showGenreDropdown = false;
  }
}

selectItem(item: string, type: 'genre' | 'actor'): void {
  const selection = type === 'genre' ? this.selectedGenres : this.selectedActors;

  if (selection.includes(item)) {
    const index = selection.indexOf(item);
    selection.splice(index, 1);
  } else if (selection.length < 2) {
    selection.push(item);
  }

  if (type === 'genre') {
    this.selectedGenres = [...selection];
  } else {
    this.selectedActors = [...selection];
  }
}
}


