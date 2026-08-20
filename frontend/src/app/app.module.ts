import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';


@NgModule({

  declarations: [
    AppComponent
  ],

  imports: [

    // Angular
    BrowserModule,

    // Routing
    AppRoutingModule,

    // Required for [(ngModel)]
    FormsModule,

    // Required for HTTP GET / POST
    HttpClientModule

  ],

  providers: [],

  bootstrap: [
    AppComponent
  ]

})


export class AppModule {}