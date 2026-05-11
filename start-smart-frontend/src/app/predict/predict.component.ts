import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { StudentService } from '../student.service';
import Chart from 'chart.js/auto';

@Component({
    selector: 'app-predict',
    templateUrl: './predict.component.html',
    styleUrls: ['./predict.component.css']
})
export class PredictComponent implements OnInit {
    predictForm!: FormGroup;
    activeStep = 1;
    loading = false;
    radarChart: any;

    @ViewChild('radarCanvas') radarCanvas!: ElementRef;

    fields = [
        { id: 'Informatique', label: 'Computer Science', icon: '💻' },
        { id: 'Génie Civil', label: 'Civil Engineering', icon: '🏗️' },
        { id: 'Génie Électrique', label: 'Electrical Engineering', icon: '⚡' },
        { id: 'Génie Mécanique', label: 'Mechanical Engineering', icon: '⚙️' },
        { id: 'Mathématiques', label: 'Mathematics', icon: '📐' }
    ];

    learningStyles = [
        { id: 'Visual', label: 'Visual', icon: '👁️' },
        { id: 'Auditory', label: 'Auditory', icon: '👂' },
        { id: 'Kinesthetic', label: 'Kinesthetic', icon: '🤲' },
        { id: 'Reading', label: 'Reading', icon: '📖' }
    ];

    constructor(
        private fb: FormBuilder,
        private studentService: StudentService,
        private router: Router
    ) { }

    ngOnInit(): void {
        this.predictForm = this.fb.group({
            // Step 1: Profil
            age: [20, [Validators.required, Validators.min(17), Validators.max(30)]],
            bac_grade: [13.00, [Validators.required, Validators.min(0), Validators.max(20)]],
            gender: ['M', Validators.required],
            field: ['Informatique', Validators.required],
            learning_style: ['Visual', Validators.required],
            initial_level: ['Intermediate', Validators.required],

            // Step 2: Performances
            overall_quiz_performance: [55, Validators.required],
            midterm_exam_score: [50, Validators.required],
            concept_mastery_rate_final: [50, Validators.required],
            early_avg_score: [50, Validators.required],
            performance_consistency: [10, Validators.required],

            // Step 3: Engagement
            attendance_rate_avg: [75, Validators.required],
            login_frequency_avg: [4, Validators.required],
            time_spent_platform_avg: [8, Validators.required],
            video_completion_rate_avg: [60, Validators.required],
            exercise_completion_rate_avg: [55, Validators.required],
            assignment_submission_rate_avg: [70, Validators.required],
            engagement_score: [15, Validators.required],

            // Step 4: Games & AI
            brainrush_games_played_total: [60, Validators.required],
            brainrush_avg_score_avg: [45, Validators.required],
            ai_chat_sessions_total: [20, Validators.required],
            ai_feedback_rating_avg: [3.5, Validators.required],

            // Step 5: Early Signals
            early_login_frequency: [4, Validators.required],
            early_attendance_rate: [80, Validators.required],
            early_dropout_probability: [0.3, Validators.required]
        });

        this.predictForm.valueChanges.subscribe(() => {
            this.updateRadar();
        });
    }

    setStep(step: number) {
        this.activeStep = step;
        if (step === 5) {
            setTimeout(() => this.initRadar(), 0);
        }
    }

    initRadar() {
        if (this.radarChart) return;
        const ctx = this.radarCanvas.nativeElement.getContext('2d');
        this.radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Quiz %', 'Présence', 'Engagement', 'Maîtrise', 'Devoirs', 'IA'],
                datasets: [{
                    label: 'Profil Étudiant',
                    data: this.getRadarData(),
                    backgroundColor: 'rgba(139, 0, 0, 0.2)',
                    borderColor: '#8B0000',
                    borderWidth: 2,
                    pointBackgroundColor: '#8B0000'
                }]
            },
            options: {
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: { display: false }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    getRadarData() {
        const v = this.predictForm.value;
        return [
            v.overall_quiz_performance,
            v.attendance_rate_avg,
            (v.engagement_score / 30) * 100,
            v.concept_mastery_rate_final,
            v.assignment_submission_rate_avg,
            (v.ai_chat_sessions_total / 100) * 100
        ];
    }

    updateRadar() {
        if (this.radarChart) {
            this.radarChart.data.datasets[0].data = this.getRadarData();
            this.radarChart.update();
        }
    }

    onSubmit() {
        if (this.predictForm.valid) {
            this.loading = true;
            this.studentService.predict(this.predictForm.value).subscribe({
                next: (res) => {
                    this.loading = false;
                    this.router.navigate(['/results'], { state: { result: res } });
                },
                error: (err) => {
                    console.error(err);
                    this.loading = false;
                    alert("Erreur: Le backend n'est pas accessible. Veuillez vérifier qu'il est bien démarré.");
                }
            });
        }
    }
}
