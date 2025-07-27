import { Component } from '@angular/core';
import {NgIf} from "@angular/common";
import {Router} from "@angular/router";
import { MatToolbarModule } from '@angular/material/toolbar';
import {MatButtonModule} from "@angular/material/button";
// @ts-ignore
@Component({
  selector: 'app-navigation',
  standalone: true,
  imports: [
    NgIf,
    MatToolbarModule,
    MatButtonModule
  ],
  templateUrl: './navigation.component.html',
  styleUrl: './navigation.component.css'
})
export class NavigationComponent {

  constructor(private router: Router) {
  }
  pi1() {
    this.router.navigate(['/pi1']);
  }
  pi2() {
    this.router.navigate(['/pi2']);
  }
  pi3() {
    this.router.navigate(['/pi3']);
  }

  alarms() {
    this.router.navigate(['/alarms']);
  }
}

