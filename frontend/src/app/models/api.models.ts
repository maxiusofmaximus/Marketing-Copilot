export interface HealthResponse {
  status: string;
  dataset_loaded: boolean;
  recordings_rows: number;
  metrics_rows: number;
}

export interface ChartData {
  chart_type: 'bar' | 'horizontal_bar' | 'pie' | 'line';
  labels: string[];
  values: number[];
  label: string;
}

export interface AskResponse {
  answer: string;
  interpretation: string;
  chart_data: ChartData | null;
}

export interface TopPage {
  page: string;
  sessions: number;
  percentage: number;
  avg_engagement?: number;
  avg_duration_sec?: number;
}

export interface AbandonoMetric {
  page: string;
  exit_count: number;
  entry_count: number;
  total_appearances: number;
  exit_rate: number;
  bounce_rate?: number;
}

export interface FlujoMetric {
  sequence: string[];
  entrada: string;
  salida: string;
  count: number;
  percentage: number;
}

export interface InteraccionMetric {
  page: string;
  sessions: number;
  avg_clicks_session?: number;
  avg_clicks_page?: number;
  avg_time_page?: number;
  avg_duration?: number;
  avg_interaction?: number;
  avg_engagement?: number;
  avg_pages?: number;
}

export interface SegmentItem {
  name: string;
  count: number;
  percentage: number;
}

export interface Segmentation {
  by_device?: SegmentItem[];
  by_country?: SegmentItem[];
  by_browser?: SegmentItem[];
  by_os?: SegmentItem[];
  traffic_source?: {
    external: number;
    direct: number;
    external_pct: number;
  };
}

export interface TrapPage {
  page: string;
  sessions: number;
  avg_engagement?: number;
  bounce_rate?: number;
  avg_duration?: number;
  trap_score: number;
}

export interface FrustrationData {
  source: string;
  frustrated_sessions?: number;
  total_sessions?: number;
  frustration_rate?: number;
  top_frustrated_pages?: { page: string; count: number }[];
  by_metric?: Record<string, any[]>;
}

export interface HourlyEngagement {
  hour: number;
  sessions: number;
  avg_engagement?: number;
  avg_duration?: number;
  bounce_rate?: number;
}

export interface ConversionMetric {
  conversion_page: string;
  sessions_reached: number;
  total_sessions: number;
  reach_rate: number;
  avg_engagement?: number;
  bounce_rate?: number;
  top_entry_pages?: { page: string; count: number }[];
}

export interface DashboardSummary {
  total_sessions: number;
  unique_users?: number;
  avg_pages_per_session?: number;
  avg_duration_seconds?: number;
  avg_engagement_score?: number;
  bounce_rate?: number;
  bounced_sessions?: number;
  avg_clicks_per_session?: number;
  frustration_rate?: number;
  home_entry_rate?: number;
  external_traffic_rate?: number;
  date_range?: { start: string; end: string };
}

export interface DashboardResponse {
  summary: DashboardSummary;
  top_pages: TopPage[];
  abandono: AbandonoMetric[];
  flujos: FlujoMetric[];
  interaccion: InteraccionMetric[];
  conversion: ConversionMetric[];
  segmentation: Segmentation;
  trap_pages: TrapPage[];
  frustration: FrustrationData;
  engagement_hourly: HourlyEngagement[];
}

export interface SuggestedQuestions {
  questions: string[];
}
