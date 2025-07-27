import {Component, OnInit} from '@angular/core';
import {Edit} from "../../model/edit";
import {Socket} from "socket.io-client";
import {WebsocketService} from "../../../service/websocket.service";

@Component({
  selector: 'app-pi2',
  standalone: true,
  imports: [],
  templateUrl: './pi2.component.html',
  styleUrl: './pi2.component.css'
})
export class Pi2Component implements OnInit {

  dht3: Edit[] = [];
  gdht: Edit[] = [];
  gyro: Edit[] = [];
  ds2: Edit = {} as Edit;
  rpir3: Edit = {} as Edit;
  dpir2: Edit = {} as Edit;
  dus2: Edit = {} as Edit;

  constructor(private socketService: WebsocketService) {}


  ngOnInit(): void {

    this.socketService.listen('update/PI2').subscribe((dataRaw: any) => {
      const data = typeof dataRaw === 'string' ? JSON.parse(dataRaw) : dataRaw;

      switch (data["name"]) {
        case "RDHT3" :
          this.updateDHT(data, this.dht3);
          break;
        case "GDHT" :
          this.updateDHT(data, this.gdht);
          break;
        case "BUTTON2":
          this.ds2 = data;
          break;
        case "DPIR2":
          this.dpir2 = data;
          break;
        case "RPIR3":
          this.rpir3 = data;
          break;
        case "DUS2":
          this.dus2 = data;
          break
        case "GSG":
          this.updateGyro(data);
          break
      }
      // Handle received data
      console.log('Received Socket.IO message:', data);
    });
  }

  updateGyro(data: Edit) {
    if (data["axis"] == "x") {
      this.gyro[0] = data;
    } else if (data["axis"] == "y") {
      this.gyro[1] = data;
    } else {
      this.gyro[2] = data;
    }
  }

  updateDHT(data: Edit, dht: Edit[]) {
    if (data["measurement"].toLowerCase() == "temperature") {
      dht[0] = data;
    } else {
      dht[1] = data;
    }
  }
}
