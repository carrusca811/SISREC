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

  constructor(private router: Router) {
    this.formRegister = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [Validators.required, Validators.minLength(6)]),
    });
  }

  ngOnInit(): void {}

  onSubmit(): void {
    if (this.formRegister.valid) {
      const { email, password } = this.formRegister.value;
      const users = JSON.parse(localStorage.getItem('users') || '[]');

      const userExists = users.some((u: any) => u.email === email);

      if (userExists) {
        this.registerError = 'Este email já está registado.';
      } else {
        users.push({ email, password });
        localStorage.setItem('users', JSON.stringify(users));
        this.registerError = null;
        this.router.navigate(['/login']);
      }
    } else {
      this.registerError = 'Preencha todos os campos corretamente.';
    }
  }
}
