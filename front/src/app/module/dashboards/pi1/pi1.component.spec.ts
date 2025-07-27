import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Pi1Component } from './pi1.component';

describe('Pi1Component', () => {
  let component: Pi1Component;
  let fixture: ComponentFixture<Pi1Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Pi1Component]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(Pi1Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
