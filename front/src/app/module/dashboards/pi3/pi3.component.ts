import {Component, OnInit} from '@angular/core';
import {Edit} from "../../model/edit";
import {Socket} from "socket.io-client";
import {WebsocketService} from "../../../service/websocket.service";

@Component({
  selector: 'app-pi3',
  standalone: true,
  imports: [],
  templateUrl: './pi3.component.html',
  styleUrl: './pi3.component.css'
})
export class Pi3Component implements OnInit{
  dht4: Edit[] = [];
  bb: Edit = {} as Edit;
  rpir4: Edit = {} as Edit;
  rgb: Edit = {} as Edit;

  constructor(private socketService: WebsocketService) {}
  ngOnInit(): void {
    this.socketService.listen('update/PI3').subscribe((dataRaw: any) => {
      const data = typeof dataRaw === 'string' ? JSON.parse(dataRaw) : dataRaw;
      console.log("DATA ", data)
      switch (data["name"]) {
        case "RDHT4" :
          this.updateDHT(data, this.dht4);
          break;
        case "RPIR4":
          this.rpir4 = data;
          break;
        case "Buzzer2":
          this.bb = data;
          break;
        case "BRGB":
          this.rgb = data;
          break;

      }
      // Handle received data
      console.log('Received Socket.IO message:', data);
    });
  }

  updateDHT(data: Edit, dht: Edit[]) {
    if (data["measurement"].toLowerCase() == "temperature") {
      dht[0] = data;
    } else {
      dht[1] = data;
    }
  }
}
