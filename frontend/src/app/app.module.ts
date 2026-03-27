import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { CopilotComponent } from './components/copilot/copilot.component';
import { AnalyticsComponent } from './components/analytics/analytics.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { KpiCardComponent } from './components/kpi-card/kpi-card.component';
import { ChartComponent } from './components/chart/chart.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    CopilotComponent,
    AnalyticsComponent,
    SidebarComponent,
    KpiCardComponent,
    ChartComponent,
  ],
  imports: [
    BrowserModule,
    CommonModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
