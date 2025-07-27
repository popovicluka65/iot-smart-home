import {Component, NgZone, OnInit} from '@angular/core';
import {WebsocketService} from "../../../service/websocket.service";
import {Subscription} from "rxjs";
import {NgClass, NgForOf, NgIf, UpperCasePipe} from "@angular/common";
import {HttpClient, HttpClientModule} from "@angular/common/http";
import {FormsModule} from "@angular/forms";
import {MatSnackBar, MatSnackBarModule} from '@angular/material/snack-bar';
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";


@Component({
  selector: 'app-alarm-display',
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    HttpClientModule,
    NgClass,
    NgForOf,
    UpperCasePipe,
    MatSnackBarModule
  ],
  templateUrl: './alarm-display.component.html',
  styleUrl: './alarm-display.component.css'
})
export class AlarmDisplayComponent  implements OnInit{
  time: string = '';
  temperature: number | null = null;
  humidity: number | null = null;
  timestamp: string = '';

  alarmActive: boolean = false;
  pinCode: string = '';
  message: string = '';

  alarmDate: string = '';
  alarmTimeSet: string = '';


  availableColors: string[] = [
    'off', 'red', 'blue', 'purple', 'white', 'yellow', 'light blue', 'green'
  ];
  currentColor: string = 'off';
  peopleCount: number = 0;

  alarmSnackbarVisible = false;
  buzzerSnackbarVisible = false;
  alarmSnackbarTimeout?: any;
  buzzerSnackbarTimeout?: any;

  constructor(private socketService: WebsocketService, private http: HttpClient,private ngZone: NgZone) {}

  ngOnInit(): void {
    this.socketService.listen('B4SD').subscribe((data) => {
      this.time = data['value'];
      console.log('B4SD time:', this.time);
    });


    this.socketService.listen('people_update').subscribe((data: any) => {
      console.log('People update received:', data);
      this.peopleCount = data.count;
    });


    this.socketService.listen('lcd_data').subscribe(data => {
      if (data.measurement === 'Temperature') {
        this.temperature = data.value;
      } else if (data.measurement === 'Humidity') {
        this.humidity = data.value;
      }
      this.timestamp = data.datetime;
    });

    // Listen for alarm status updates (e.g. from backend or sensors)
    this.socketService.listen('alarm_status').subscribe(data => {
      this.alarmActive = data.isActive;
      console.log('Alarm status updated:', this.alarmActive);
    });

    this.socketService.listen('rgb_status').subscribe(data => {
      this.currentColor = data.color;
      console.log('RGB status updated:', this.currentColor);
    });

    this.socketService.listen('buzzer').subscribe((dataRaw) => {
      console.log("POGODI BUZZER")
      const data = typeof dataRaw === 'string' ? JSON.parse(dataRaw) : dataRaw;
      console.log('Buzzer data:', data);
      if (data["value"]==true){
        console.log("UDJE U ON")
        this.showBuzzerSnackbar();
      }

      if (data.status?.trim().toUpperCase() === 'ON') {
        console.log("UDJE OVDE2")
        this.showBuzzerSnackbar();
      } else if (data.status?.trim().toUpperCase() === 'OFF') {
        //this.hideSnackbar();
        console.log("UDJE OVDE 3")
      }

    });

    this.socketService.listen('alarm').subscribe((data: any) => {
      console.log('Alarm event primljen:', data);

      try {
        const parsed = typeof data === 'string' ? JSON.parse(data) : data;
        console.log('Parsed data:', parsed);

        this.ngZone.run(() => {
          console.log("Status:", parsed.status);
          console.log(`Status: '${parsed.status}' (length: ${parsed.status?.length})`);
          if (parsed.status?.trim().toUpperCase() === 'ON') {
            this.showAlarmSnackbar();
          } else if (parsed.status?.trim().toUpperCase() === 'OFF') {
            this.alarmSnackbarVisible = false;
            if (this.alarmSnackbarTimeout) {
              clearTimeout(this.alarmSnackbarTimeout);
            }
          }
        });
      } catch(e) {
        console.error('Error parsing websocket data:', e);
      }
    });

  }

  sendPin() {
    if (this.pinCode.length !== 4) {
      this.message = 'PIN mora imati 4 cifre.';
      return;
    }

    this.http.put('http://localhost:5000/dms/code', { code: this.pinCode }).subscribe({
      next: (res: any) => {
        this.message = res.message || 'PIN poslat.';
        this.pinCode = '';
      },
      error: (err) => {
        console.error(err);
        this.message = 'Greška prilikom slanja PIN-a.';
      }
    });
  }

  setRgbColor(color: string) {
    this.http.put('http://localhost:5000/rgb/color', {color}).subscribe({
      next: (res: any) => {
        this.message = res.message || `Boja promenjena na ${color}`;
        this.currentColor = color;
      },
      error: (err) => {
        console.error(err);
        this.message = 'Greška prilikom promene boje.';
      }
    });
  }

  setClockAlarm() {
    const params = {
      date: this.alarmDate,
      time: this.alarmTimeSet
    }
    this.http.post('http://localhost:5000/clock-alarm', { params }).subscribe({
      next: (res: any) => {
        this.message = res.message || 'Budilnik podešen.';
        console.log('Alarm response:', res);
      },
      error: (err) => {
        console.error(err);
        this.message = 'Greška prilikom podešavanja budilnika.';
      }
    });
  };

  turnClockAlarmOff() {
    this.http.put('http://localhost:5000/clock-alarm/off', {}).subscribe({
      next: (res: any) => {
        this.message = res.message || 'Budilnik isključen.';
        console.log('Alarm OFF response:', res);
        this.buzzerSnackbarVisible = false;
      },
      error: (err) => {
        console.error(err);
        this.message = 'Greška prilikom isključivanja budilnika.';
      }
    });
  }
  showBuzzerSnackbar(): void {
    this.buzzerSnackbarVisible = true;
  }


  hideSnackbar(): void {
    this.buzzerSnackbarVisible = false;
    if (this.buzzerSnackbarTimeout) {
      clearTimeout(this.buzzerSnackbarTimeout);
    }
  }
  showAlarmSnackbar(): void {
    this.message = '🛑 Alarm je aktiviran! Isključi ga!';

    // Ako je snackbar već vidljiv, resetuj timeout
    if (this.alarmSnackbarTimeout) {
      clearTimeout(this.alarmSnackbarTimeout);
    }

    // Prikaži snackbar
    this.alarmSnackbarVisible = true;

    // Postavi novi timeout za automatsko skrivanje
    // this.alarmSnackbarTimeout = setTimeout(() => {
    //   this.alarmSnackbarVisible = false;
    // }, 3000);
  }



  turnOffAlarm() {
    this.http.put('http://localhost:5000/alarm-off', {}, {
      headers: { 'Content-Type': 'application/json' }
    }).subscribe({
      next: (res: any) => {
        this.message = res.message || 'Alarm isključen.';
        console.log('Alarm OFF response:', res);
        this.alarmSnackbarVisible = false;
      },
      error: (err) => {
        console.error('Greška prilikom gašenja alarma:', err);
        this.message = 'Greška prilikom isključivanja alarma.';
      }
    });
  }



}
