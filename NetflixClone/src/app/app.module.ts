import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { HomeComponent } from './pages/home/home.component';
import { MovieDetailsComponent } from './pages/movie-details/movie-details.component';
import { SearchComponent } from './pages/search/search.component';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { MoviesSliderComponent } from './pages/movies-slider/movies-slider.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';

import { MoviesService } from './services/movies.service';
import { AuthGuard } from './auth.guard';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    MovieDetailsComponent,
    SearchComponent,
    NavbarComponent,
    MoviesSliderComponent,
    LoginComponent,
    RegisterComponent,
    BrowserModule,
    FormsModule,
    DropdownModule,
    BrowserAnimationsModule
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
  ],
  providers: [
    MoviesService,
    AuthGuard
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
