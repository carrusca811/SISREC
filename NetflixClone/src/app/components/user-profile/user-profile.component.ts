import { Component, OnInit } from '@angular/core';
import { AppStorageService } from 'src/app/services/app.storage.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss'],
  standalone: false,
})
export class UserProfileComponent implements OnInit {

  user: any;
  reviewedMovies: any[] = [];

  constructor(
    private storageService: AppStorageService,
    private userService: UserService
  ) {}

  ngOnInit(): void {
    this.user = this.storageService.getItem('user');
    const userId = this.user?.id || this.user?._id;

    if (!userId) return;

    this.getUserDetails(userId);
    this.loadReviewedMovies(userId);
  }

  getUserDetails(userId: string): void {
    this.userService.getUserById(userId).subscribe({
      next: (user) => {
        this.user = user;
        this.storageService.setItem('user', user);
        console.log("👤 Detalhes do usuário:", user);
      },
      error: (err) => {
        console.error("Erro ao buscar detalhes do usuário:", err);
      }
    });
  }

  loadReviewedMovies(userId: string): void {
    this.userService.getUserReviewedMovies(userId).subscribe({
      next: (movies) => {
        this.reviewedMovies = movies;
        console.log("🎬 Filmes avaliados:", movies);
      },
      error: (err) => {
        console.error("Erro ao buscar filmes avaliados:", err);
      }
    });
  }

  chunk(array: any[], size: number): any[][] {
    const result: any[][] = [];
    for (let i = 0; i < array.length; i += size) {
      result.push(array.slice(i, i + size));
    }
    return result;
  }
  

}
