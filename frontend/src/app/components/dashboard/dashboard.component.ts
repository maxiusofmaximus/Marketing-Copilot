import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { DashboardResponse, ChartData } from '../../models/api.models';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  data: DashboardResponse | null = null;
  loading = true;

  deviceChart: ChartData | null = null;
  countryChart: ChartData | null = null;
  hourlyChart: ChartData | null = null;
  topPagesChart: ChartData | null = null;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.dashboard().subscribe({
      next: (res) => {
        this.data = res;
        this.buildCharts(res);
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  private buildCharts(res: DashboardResponse) {
    const seg = res.segmentation;

    if (seg.by_device?.length) {
      this.deviceChart = {
        chart_type: 'pie',
        labels: seg.by_device.map(d => d.name),
        values: seg.by_device.map(d => d.count),
        label: 'Dispositivos'
      };
    }

    if (seg.by_country?.length) {
      this.countryChart = {
        chart_type: 'horizontal_bar',
        labels: seg.by_country.slice(0, 8).map(d => d.name),
        values: seg.by_country.slice(0, 8).map(d => d.count),
        label: 'Sesiones'
      };
    }

    if (res.engagement_hourly?.length) {
      this.hourlyChart = {
        chart_type: 'line',
        labels: res.engagement_hourly.map(h => `${h.hour}:00`),
        values: res.engagement_hourly.map(h => h.sessions),
        label: 'Sesiones'
      };
    }

    if (res.top_pages?.length) {
      this.topPagesChart = {
        chart_type: 'horizontal_bar',
        labels: res.top_pages.slice(0, 8).map(p => p.page),
        values: res.top_pages.slice(0, 8).map(p => p.sessions),
        label: 'Sesiones'
      };
    }
  }

  formatDuration(secs: number | undefined): string {
    if (!secs) return '—';
    const m = Math.floor(secs / 60);
    const s = Math.round(secs % 60);
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  }

  formatNum(n: number | undefined): string {
    if (n === undefined || n === null) return '—';
    return n.toLocaleString('es-CO');
  }
}
