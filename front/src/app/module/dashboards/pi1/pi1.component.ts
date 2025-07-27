import {Component, OnInit} from '@angular/core';
import {Socket} from "socket.io-client";
import {Edit} from "../../model/edit";
import {WebsocketService} from "../../../service/websocket.service";

@Component({
  selector: 'app-pi1',
  standalone: true,
  imports: [],
  templateUrl: './pi1.component.html',
  styleUrl: './pi1.component.css'
})
export class Pi1Component  implements OnInit{

  dht1: Edit[] = [];
  dht2: Edit[] = [];
  dl: Edit = {} as Edit;
  uds1: Edit= {} as Edit;
  rpir1:Edit = {} as Edit;
  rpir2: Edit = {} as Edit;
  dpir1: Edit = {} as Edit;
  db: Edit = {} as Edit;
  ds1: Edit = {} as Edit;
  constructor(private socketService: WebsocketService) {}


    ngOnInit(): void {
      this.socketService.listen('update/PI1').subscribe((dataRaw: any) => {
        const data = typeof dataRaw === 'string' ? JSON.parse(dataRaw) : dataRaw;
        console.log("DATA", data);

        switch (data["name"]) {
          case "RDHT1":
            this.updateDHT(data, this.dht1);
            break;
          case "RDHT2":
            this.updateDHT(data, this.dht2);
            break;
          case "LED":
            this.dl = data;
            break;
          case "DUS1":
            this.uds1 = data;
            break;
          case "RPIR1":
            this.rpir1 = data;
            break;
          case "RPIR2":
            this.rpir2 = data;
            break;
          case "DPIR1":
            this.dpir1 = data;
            break;
          case "Buzzer":
            this.db = data;
            break;
          case "BUTTON1":
            this.ds1 = data;
            break;
        }

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
