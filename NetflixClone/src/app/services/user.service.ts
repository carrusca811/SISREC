import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseURL = 'http://127.0.0.1:8000';
  private authState = new BehaviorSubject<boolean>(this.hasUser());

  constructor(private http: HttpClient, private router: Router) {}

  get isLoggedIn$(): Observable<boolean> {
    return this.authState.asObservable();
  }

  private hasUser(): boolean {
    return !!localStorage.getItem('user');
  }

  login(credentials: { email: string; password: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      this.http.post(`${this.baseURL}/login`, credentials).subscribe({
        next: (response: any) => {
          localStorage.setItem('user', JSON.stringify(response));
          this.authState.next(true);
          resolve();
        },
        error: (err) => {
          console.error('Login error:', err);
          reject('Credenciais inválidas');
        }
      });
    });
  }

  register(user: { email: string, password: string, preference_genre?: string[], preference_actor?: string[] }): Promise<any> {
    const url = `${this.baseURL}/register`;
    return this.http.post(url, user).toPromise();
  }
  

  logout(): Promise<void> {
    return new Promise((resolve) => {
      localStorage.removeItem('user');
      this.authState.next(false);
      this.router.navigate(['/login']);
      resolve();
    });
  }

  getCurrentUser(): any | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }


  updatePreferences(preferences: { user_id: string, preference_genre: string[], preference_actor: string[] }): Promise<any> {
    const url = `${this.baseURL}/update-preferences`;
    return this.http.put(url, preferences).toPromise();
  }
  
}
