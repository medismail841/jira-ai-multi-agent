import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface JiraTicket {

  key: string;

  summary: string;

  description: string;

  status: string;

  priority: string;

  issue_type: string;

  assignee: string;

  project: {
    name: string;
    key: string;
  };

}


@Injectable({
  providedIn: 'root'
})
export class JiraService {

  private apiUrl =
    'http://localhost:8000/api/jira';


  constructor(
    private http: HttpClient
  ) {}


  getTicket(
    issueKey: string
  ): Observable<JiraTicket> {

    return this.http.get<JiraTicket>(
      `${this.apiUrl}/${issueKey}`
    );

  }

}