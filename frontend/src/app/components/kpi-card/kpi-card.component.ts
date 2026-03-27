import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-kpi-card',
  templateUrl: './kpi-card.component.html',
  styleUrls: ['./kpi-card.component.scss'],
})
export class KpiCardComponent {
  @Input() title = '';
  @Input() value: string | number = '—';
  @Input() subtitle = '';
  @Input() icon = '';
  @Input() accent: 'default' | 'success' | 'warning' | 'danger' = 'default';
}
