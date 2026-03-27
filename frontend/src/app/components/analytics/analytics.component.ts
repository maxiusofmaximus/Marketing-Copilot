import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import {
  TopPage, AbandonoMetric, InteraccionMetric,
  ConversionMetric, TrapPage, FrustrationData,
  Segmentation, ChartData
} from '../../models/api.models';

type Tab = 'pages' | 'abandono' | 'interaccion' | 'conversion' | 'trampa' | 'frustracion' | 'segmentacion';

@Component({
  selector: 'app-analytics',
  templateUrl: './analytics.component.html',
  styleUrls: ['./analytics.component.scss'],
})
export class AnalyticsComponent implements OnInit {
  activeTab: Tab = 'pages';
  loading = false;

  topPages: TopPage[] = [];
  abandono: AbandonoMetric[] = [];
  interaccion: InteraccionMetric[] = [];
  conversion: ConversionMetric[] = [];
  trapPages: TrapPage[] = [];
  frustration: FrustrationData | null = null;
  segmentation: Segmentation | null = null;

  pagesChart: ChartData | null = null;
  abandonoChart: ChartData | null = null;
  conversionChart: ChartData | null = null;

  tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'pages',        label: 'Top Páginas',    icon: '📄' },
    { id: 'abandono',     label: 'Abandono',        icon: '🚪' },
    { id: 'interaccion',  label: 'Interacción',     icon: '🖱️' },
    { id: 'conversion',   label: 'Conversión',      icon: '🎯' },
    { id: 'trampa',       label: 'Páginas Trampa',  icon: '⚠️' },
    { id: 'frustracion',  label: 'Frustración',     icon: '😤' },
    { id: 'segmentacion', label: 'Segmentación',    icon: '🌎' },
  ];

  constructor(private api: ApiService) {}

  ngOnInit() { this.loadTab('pages'); }

  selectTab(tab: Tab) {
    this.activeTab = tab;
    this.loadTab(tab);
  }

  private loadTab(tab: Tab) {
    this.loading = true;
    switch (tab) {
      case 'pages':
        this.api.topPages(15).subscribe(r => {
          this.topPages = r.data;
          this.pagesChart = {
            chart_type: 'horizontal_bar',
            labels: r.data.slice(0, 10).map(p => p.page),
            values: r.data.slice(0, 10).map(p => p.sessions),
            label: 'Sesiones'
          };
          this.loading = false;
        });
        break;
      case 'abandono':
        this.api.abandono(15).subscribe(r => {
          this.abandono = r.data;
          this.abandonoChart = {
            chart_type: 'bar',
            labels: r.data.slice(0, 10).map(p => p.page),
            values: r.data.slice(0, 10).map(p => p.exit_count),
            label: 'Salidas'
          };
          this.loading = false;
        });
        break;
      case 'interaccion':
        this.api.interaccion(15).subscribe(r => { this.interaccion = r.data; this.loading = false; });
        break;
      case 'conversion':
        this.api.conversion().subscribe(r => {
          this.conversion = r.data;
          this.conversionChart = {
            chart_type: 'bar',
            labels: r.data.map(p => p.conversion_page),
            values: r.data.map(p => p.reach_rate),
            label: 'Tasa de alcance (%)'
          };
          this.loading = false;
        });
        break;
      case 'trampa':
        this.api.trapPages(15).subscribe(r => { this.trapPages = r.data; this.loading = false; });
        break;
      case 'frustracion':
        this.api.frustration(10).subscribe(r => { this.frustration = r.data; this.loading = false; });
        break;
      case 'segmentacion':
        this.api.segmentation().subscribe(r => { this.segmentation = r.data; this.loading = false; });
        break;
    }
  }

  trapColor(score: number): string {
    if (score > 0.66) return 'badge-danger';
    if (score > 0.33) return 'badge-warning';
    return 'badge-success';
  }

  fmt(n: number | undefined, decimals = 1): string {
    if (n === undefined || n === null) return '—';
    return typeof n === 'number' ? n.toFixed(decimals) : String(n);
  }

  fmtNum(n: number | undefined): string {
    if (n === undefined || n === null) return '—';
    return n.toLocaleString('es-CO');
  }
}
