import {
  Component, Input, OnChanges, OnDestroy,
  AfterViewInit, ElementRef, ViewChild
} from '@angular/core';
import { Chart, ChartType, registerables } from 'chart.js';
import { ChartData } from '../../models/api.models';

Chart.register(...registerables);

@Component({
  selector: 'app-chart',
  template: `<canvas #canvas></canvas>`,
  styles: [`canvas { width: 100% !important; }`]
})
export class ChartComponent implements OnChanges, OnDestroy, AfterViewInit {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  @Input() data: ChartData | null = null;
  @Input() height = 260;

  private chart: Chart | null = null;
  private ready = false;

  ngAfterViewInit() {
    this.ready = true;
    if (this.data) this.render();
  }

  ngOnChanges() {
    if (this.ready && this.data) this.render();
  }

  ngOnDestroy() {
    this.chart?.destroy();
  }

  private render() {
    this.chart?.destroy();
    if (!this.data || !this.canvasRef) return;

    const canvas = this.canvasRef.nativeElement;
    canvas.height = this.height;

    const typeMap: Record<string, ChartType> = {
      bar: 'bar', horizontal_bar: 'bar', pie: 'pie', line: 'line'
    };

    const isHorizontal = this.data.chart_type === 'horizontal_bar';

    const accent = '#6366f1';
    const colors = this.data.chart_type === 'pie'
      ? ['#6366f1','#22c55e','#f59e0b','#ef4444','#06b6d4','#a855f7','#ec4899','#14b8a6','#f97316','#84cc16']
      : Array(this.data.values.length).fill(accent);

    this.chart = new Chart(canvas, {
      type: typeMap[this.data.chart_type] || 'bar',
      data: {
        labels: this.data.labels,
        datasets: [{
          label: this.data.label,
          data: this.data.values,
          backgroundColor: colors,
          borderColor: this.data.chart_type === 'line' ? accent : colors,
          borderWidth: this.data.chart_type === 'line' ? 2 : 0,
          borderRadius: this.data.chart_type === 'pie' ? 0 : 6,
          tension: 0.4,
          fill: this.data.chart_type === 'line',
          pointBackgroundColor: accent,
        }]
      },
      options: {
        indexAxis: isHorizontal ? 'y' : 'x',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: this.data.chart_type === 'pie', labels: { color: '#94a3b8', font: { size: 12 } } },
          tooltip: {
            backgroundColor: '#21253a',
            borderColor: 'rgba(255,255,255,0.07)',
            borderWidth: 1,
            titleColor: '#f1f5f9',
            bodyColor: '#94a3b8',
          }
        },
        scales: this.data.chart_type === 'pie' ? {} : {
          x: { ticks: { color: '#475569', maxRotation: 45 }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { ticks: { color: '#475569' }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  }
}
