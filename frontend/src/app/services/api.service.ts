import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  AskResponse, DashboardResponse, HealthResponse,
  TopPage, AbandonoMetric, FlujoMetric, InteraccionMetric,
  ConversionMetric, Segmentation, TrapPage, FrustrationData,
  HourlyEngagement, SuggestedQuestions
} from '../models/api.models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.base}/health`);
  }

  dashboard(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(`${this.base}/dashboard`);
  }

  ask(question: string): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.base}/ask`, { question });
  }

  suggestedQuestions(): Observable<SuggestedQuestions> {
    return this.http.get<SuggestedQuestions>(`${this.base}/suggested-questions`);
  }

  topPages(limit = 10): Observable<{ data: TopPage[] }> {
    return this.http.get<{ data: TopPage[] }>(`${this.base}/pages/top?limit=${limit}`);
  }

  abandono(limit = 10): Observable<{ data: AbandonoMetric[] }> {
    return this.http.get<{ data: AbandonoMetric[] }>(`${this.base}/abandono?limit=${limit}`);
  }

  flujos(limit = 10): Observable<{ data: FlujoMetric[] }> {
    return this.http.get<{ data: FlujoMetric[] }>(`${this.base}/flujos?limit=${limit}`);
  }

  interaccion(limit = 15): Observable<{ data: InteraccionMetric[] }> {
    return this.http.get<{ data: InteraccionMetric[] }>(`${this.base}/interaccion?limit=${limit}`);
  }

  conversion(): Observable<{ data: ConversionMetric[] }> {
    return this.http.get<{ data: ConversionMetric[] }>(`${this.base}/conversion`);
  }

  segmentation(): Observable<{ data: Segmentation }> {
    return this.http.get<{ data: Segmentation }>(`${this.base}/segmentation`);
  }

  trapPages(limit = 10): Observable<{ data: TrapPage[] }> {
    return this.http.get<{ data: TrapPage[] }>(`${this.base}/trap-pages?limit=${limit}`);
  }

  frustration(limit = 10): Observable<{ data: FrustrationData }> {
    return this.http.get<{ data: FrustrationData }>(`${this.base}/frustration?limit=${limit}`);
  }

  engagementHourly(): Observable<{ data: HourlyEngagement[] }> {
    return this.http.get<{ data: HourlyEngagement[] }>(`${this.base}/engagement-hourly`);
  }
}
