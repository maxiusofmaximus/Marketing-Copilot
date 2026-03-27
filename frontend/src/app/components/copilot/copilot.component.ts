import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AskResponse } from '../../models/api.models';

interface Message {
  role: 'user' | 'bot';
  text: string;
  interpretation?: string;
  chart?: AskResponse['chart_data'];
  timestamp: Date;
}

@Component({
  selector: 'app-copilot',
  templateUrl: './copilot.component.html',
  styleUrls: ['./copilot.component.scss'],
})
export class CopilotComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;

  messages: Message[] = [];
  suggestedQuestions: string[] = [];
  inputText = '';
  loading = false;
  showSuggestions = true;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.suggestedQuestions().subscribe({
      next: (res) => { this.suggestedQuestions = res.questions; }
    });

    this.messages.push({
      role: 'bot',
      text: '¡Hola! Soy tu Co-piloto de Marketing 🤖\nPuedo analizar el comportamiento de los usuarios en CloudLabs y darte insights accionables. ¿Qué quieres saber?',
      timestamp: new Date(),
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  send(question?: string) {
    const q = (question ?? this.inputText).trim();
    if (!q || this.loading) return;

    this.showSuggestions = false;
    this.inputText = '';
    this.messages.push({ role: 'user', text: q, timestamp: new Date() });
    this.loading = true;

    this.api.ask(q).subscribe({
      next: (res) => {
        this.messages.push({
          role: 'bot',
          text: res.answer,
          interpretation: res.interpretation !== res.answer ? res.interpretation : undefined,
          chart: res.chart_data,
          timestamp: new Date(),
        });
        this.loading = false;
      },
      error: () => {
        this.messages.push({
          role: 'bot',
          text: '⚠️ Error al conectar con la API. Verifica que el backend esté corriendo.',
          timestamp: new Date(),
        });
        this.loading = false;
      }
    });
  }

  onKey(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); }
  }

  private scrollToBottom() {
    try { this.messagesEnd.nativeElement.scrollIntoView({ behavior: 'smooth' }); } catch {}
  }
}
