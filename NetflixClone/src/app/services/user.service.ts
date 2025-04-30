import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Observer } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class UserService {
  private authState = new BehaviorSubject<boolean>(this.hasUser());

  get isLoggedIn$(): Observable<boolean> {
    return this.authState.asObservable();
  }

  private hasUser(): boolean {
    return !!localStorage.getItem('user');
  }

  login(credentials: { email: string; password: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      const validEmail = 'carrusca811@gmail.com';
      const validPassword = 'guga1108';

      if (
        credentials.email === validEmail &&
        credentials.password === validPassword
      ) {
        localStorage.setItem('user', credentials.email);
        this.authState.next(true);
        resolve();
      } else {
        reject('Credenciais inválidas');
      }
    });
  }

  logout(): Promise<void> {
    return new Promise((resolve) => {
      localStorage.removeItem('user');
      this.authState.next(false);
      resolve();
    });
  }

  getCurrentUser(): string | null {
    return localStorage.getItem('user');
  }
}