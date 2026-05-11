import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { StudentService } from '../student.service';
import Chart from 'chart.js/auto';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, AfterViewInit {
    stats: any;
    @ViewChild('fieldChart') fieldChartRef!: ElementRef;
    @ViewChild('genderChart') genderChartRef!: ElementRef;

    constructor(private studentService: StudentService) { }

    ngOnInit(): void {
        this.studentService.getStats().subscribe(data => {
            this.stats = data;
        });
    }

    ngAfterViewInit(): void {
        if (this.stats) {
            this.initCharts();
        }
    }

    initCharts() {
        const fieldCtx = this.fieldChartRef.nativeElement.getContext('2d');
        new Chart(fieldCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(this.stats.field_dist),
                datasets: [{
                    label: 'Students by Field',
                    data: Object.values(this.stats.field_dist),
                    backgroundColor: 'rgba(99, 102, 241, 0.6)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        const genderCtx = this.genderChartRef.nativeElement.getContext('2d');
        new Chart(genderCtx, {
            type: 'doughnut',
            data: {
                labels: ['Male', 'Female'],
                datasets: [{
                    data: [this.stats.gender_dist.M, this.stats.gender_dist.F],
                    backgroundColor: ['#6366f1', '#ec4899'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } } }
            }
        });
    }
}
