import { Routes } from '@angular/router';
import {Pi1Component} from "./module/dashboards/pi1/pi1.component";
import {Pi2Component} from "./module/dashboards/pi2/pi2.component";
import {Pi3Component} from "./module/dashboards/pi3/pi3.component";
import {AlarmDisplayComponent} from "./module/alarms/alarm-display/alarm-display.component";

export const routes: Routes =[
  {path : 'pi1', component : Pi1Component},
  {path : 'pi2', component : Pi2Component},
  {path : 'pi3', component : Pi3Component},
  {path : 'alarms', component :AlarmDisplayComponent},
];
