import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Pi3Component } from './pi3.component';

describe('Pi3Component', () => {
  let component: Pi3Component;
  let fixture: ComponentFixture<Pi3Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Pi3Component]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(Pi3Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
