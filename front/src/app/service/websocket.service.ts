import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';


@Injectable({
  providedIn: 'root'
})
export class WebsocketService {

   private socket: Socket;

  constructor() {
    this.socket = io('http://localhost:5000', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('Connected to Flask-SocketIO');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from Flask-SocketIO');
    });
  }

  // Slušaj TAČAN događaj
  listen(eventName: string): Observable<any> {
    return new Observable((subscriber) => {
      this.socket.on(eventName, (data: any) => {
        console.log(`Received [${eventName}]:`, data);
        subscriber.next(data);
      });
    });
  }

  // Ako hoćeš da šalješ događaje nazad serveru
  emit(eventName: string, data: any): void {
    this.socket.emit(eventName, data);
  }

  disconnect(): void {
    this.socket.disconnect();
  }
}
