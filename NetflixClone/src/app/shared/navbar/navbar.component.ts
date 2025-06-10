import { Component, HostListener, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AppStorageService } from 'src/app/services/app.storage.service';
import { UserService } from 'src/app/services/user.service';

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.scss'],
    standalone: false
})
export class NavbarComponent implements OnInit {
  navBackground: any;
  loggedIn = false;
  currentRoute: string = '';
  @HostListener('document:scroll') scrollover () {
    console.log(document.body.scrollTop, 'scrolllength#');

    if (document.body.scrollTop > 0 || document.documentElement.scrollTop > 0) {
      this.navBackground = {
        'background-color': '#0e0e0ede'
      }
    } else {
      this.navBackground = {}
    }
  }


  constructor (private userService: UserService, private router: Router, private storageService: AppStorageService) { }

  ngOnInit(): void {
    this.userService.isLoggedIn$.subscribe((status) => {
      this.loggedIn = status;
    });
    this.router.events.subscribe(() => {
      this.currentRoute = this.router.url;
    });
  }

  onClick () {
    this.userService.logout()
      .then(() => {
        this.storageService.removeItem('user');
        this.router.navigate([ '/login' ]);
      })
      .catch(error => console.log(error));
  }
}
