import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  formLogin: FormGroup;
  loginError: string | null = null;

  constructor(private userService: UserService, private router: Router) {
    this.formLogin = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [
        Validators.required,
        Validators.minLength(6)
      ]),
    });
  }

  ngOnInit(): void {}

  onSubmit(): void {
    if (this.formLogin.valid) {
      this.userService.login(this.formLogin.value)
        .then(() => {
          this.router.navigate(['/home']);
        })
        .catch(error => {
          this.loginError = 'Email ou password inválidos.';
          console.error(error);
        });
    } else {
      this.loginError = 'Preencha todos os campos corretamente.';
    }
  }

  // Este método pode ser usado no HTML para validações dinâmicas, se quiseres
  checkControl(controlName: string, errorName: string): boolean {
    return this.formLogin.get(controlName)?.hasError(errorName) &&
           this.formLogin.get(controlName)?.touched || false;
  }

  // Este método pode ser removido se não usares mais login com Google
  onClick(): void {
    this.loginError = 'Login com Google está desativado.';
  }
}
