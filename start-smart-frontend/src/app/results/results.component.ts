import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import Chart from 'chart.js/auto';

@Component({
    selector: 'app-results',
    templateUrl: './results.component.html',
    styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
    result: any;

    constructor(private router: Router) {
        const navigation = this.router.getCurrentNavigation();
        this.result = navigation?.extras.state?.['result'];
    }

    ngOnInit(): void {
        if (!this.result) {
            this.router.navigate(['/predict']);
            return;
        }
        setTimeout(() => {
            this.initProbabilityChart();
        }, 100);
    }

    initProbabilityChart() {
        const ctx = document.getElementById('probChart') as HTMLCanvasElement;
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['High Risk', 'Medium Risk', 'Low Risk'],
                datasets: [{
                    data: [
                        this.result.risk_probabilities.High_Risk,
                        this.result.risk_probabilities.Medium_Risk,
                        this.result.risk_probabilities.Low_Risk
                    ],
                    backgroundColor: ['#8B0000', '#f1c40f', '#1a7a4a'],
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y',
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' }
                    }
                }
            }
        });
    }

    getRiskClass() {
        if (this.result.risk_level === 'High_Risk') return 'risk-high';
        if (this.result.risk_level === 'Medium_Risk') return 'risk-medium';
        return 'risk-low';
    }

    getRiskIcon() {
        if (this.result.risk_level === 'High_Risk') return '🚫';
        if (this.result.risk_level === 'Medium_Risk') return '⚠️';
        return '✅';
    }

    getRiskLabel() {
        return this.result.risk_level.replace('_', ' ');
    }

    getGaugeStyle(value: number) {
        const dash = (value / 100) * 283;
        return { 'stroke-dasharray': `${dash} 283` };
    }
}
