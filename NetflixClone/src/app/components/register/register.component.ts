import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {

  formRegister: FormGroup;
  registerError: string | null = null;
  isSelectingPreferences: boolean = false;
  selectedGenres: string[] = [];
  selectedActors: string[] = [];

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

  constructor(private service: UserService, private router: Router) {
    this.formRegister = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [Validators.required, Validators.minLength(6)]),
      preference_genre: new FormControl([]),
      preference_actor: new FormControl([])
    });
  }

  ngOnInit(): void {}

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
        .then((response) => {
          this.registerError = null;
  
          // Armazena o user_id para a seleção de preferências
          const userId = response.id;
          sessionStorage.setItem('user_id', userId);
          this.isSelectingPreferences = true;
        })
        .catch((err) => {
          this.registerError = err.message || 'Erro ao registar utilizador.';
        });
    } else {
      this.registerError = 'Preencha todos os campos corretamente.';
    }
  }
  
  savePreferences(): void {
    const userId = sessionStorage.getItem('user_id');
  
    if (!userId) {
      this.registerError = 'ID do utilizador não encontrado.';
      return;
    }
  
    if (this.selectedGenres.length === 2 && this.selectedActors.length === 2) {
      const updatedUser = {
        user_id: userId,
        preference_genre: this.selectedGenres,
        preference_actor: this.selectedActors
      };
  
      this.service.updatePreferences(updatedUser)
        .then(() => {
          sessionStorage.removeItem('user_id');
          this.isSelectingPreferences = false;
          this.router.navigate(['/login']);
        })
        .catch((err) => {
          this.registerError = err.message || 'Erro ao atualizar preferências.';
        });
    } else {
      this.registerError = 'Selecione exatamente 2 géneros e 2 atores.';
    }
  }
  


  toggleSelection(item: string, type: 'genre' | 'actor'): void {
    if (type === 'genre') {
      if (this.selectedGenres.includes(item)) {
        this.selectedGenres = this.selectedGenres.filter(genre => genre !== item);
      } else if (this.selectedGenres.length < 2) {
        this.selectedGenres.push(item);
      }
    } else {
      if (this.selectedActors.includes(item)) {
        this.selectedActors = this.selectedActors.filter(actor => actor !== item);
      } else if (this.selectedActors.length < 2) {
        this.selectedActors.push(item);
      }
    }
  }
  
}
