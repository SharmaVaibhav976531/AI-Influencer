document.addEventListener('DOMContentLoaded', function () {
    const chartDataElement = document.getElementById('chart-data');
    if (!chartDataElement) return;
    
    const data = JSON.parse(chartDataElement.textContent);
    
    function createChart(canvasId, type, labels, datasets, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: type === 'pie' ? 'right' : 'top',
                    }
                },
                ...options
            }
        });
    }

    createChart('languageChart', 'pie', data.language.labels, [{
        data: data.language.data,
        backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6c757d']
    }]);

    createChart('platformChart', 'bar', data.platform.labels, [{
        label: 'Influencers',
        data: data.platform.data,
        backgroundColor: '#0d6efd'
    }]);

    createChart('scoreChart', 'bar', data.score.labels, [{
        label: 'Classifications',
        data: data.score.data,
        backgroundColor: '#198754'
    }]);

    createChart('recommendationChart', 'pie', data.recommendation.labels, [{
        data: data.recommendation.data,
        backgroundColor: ['#198754', '#ffc107', '#dc3545', '#6c757d']
    }]);

    createChart('orientationChart', 'bar', data.orientation.labels, [{
        label: 'Classifications',
        data: data.orientation.data,
        backgroundColor: '#6f42c1'
    }]);

    createChart('followersChart', 'bar', data.followers.labels, [{
        label: 'Influencers',
        data: data.followers.data,
        backgroundColor: '#fd7e14'
    }]);

    createChart('uploadTrendChart', 'line', data.upload_trend.labels, [{
        label: 'Uploads',
        data: data.upload_trend.data,
        borderColor: '#0d6efd',
        fill: true,
        backgroundColor: 'rgba(13, 110, 253, 0.1)'
    }]);

    createChart('classificationTrendChart', 'line', data.classification_trend.labels, [{
        label: 'Classifications',
        data: data.classification_trend.data,
        borderColor: '#198754',
        fill: true,
        backgroundColor: 'rgba(25, 135, 84, 0.1)'
    }]);
});