const API_BASE = '/api';
let forecastChartInstance = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadROI();
    loadForecast();
    loadAlerts();
    loadSchedules();
});

// Helper for API calls
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    return res.json();
}

// 1. Productivity & ROI
async function loadROI() {
    const data = await fetchAPI('/productivity/roi-ranking');
    const list = document.getElementById('roi-list');
    list.innerHTML = '';
    data.forEach(item => {
        list.innerHTML += `<li><span>${item.name} (${item.department})</span> <span>ROI: ${item.roi_score.toFixed(2)}%</span></li>`;
    });

    const rev = await fetchAPI('/productivity/revenue-per-employee');
    if(rev.length > 0) {
        document.getElementById('global-rev').innerText = `$${rev[0].revenue_attributed.toFixed(2)}`;
    }
}

async function calculateProductivity() {
    await fetchAPI('/productivity/calculate', 'POST');
    loadROI();
}

// 2. Forecasting
async function loadForecast() {
    const data = await fetchAPI('/forecast/labor-costs');
    renderChart(data);
}

async function generateForecast() {
    await fetchAPI('/forecast/generate', 'POST');
    loadForecast();
}

function renderChart(data) {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    const labels = data.map(d => d.forecast_month);
    const preds = data.map(d => d.predicted_cost);
    const lowers = data.map(d => d.confidence_lower);
    const uppers = data.map(d => d.confidence_upper);

    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Cost',
                    data: preds,
                    borderColor: 'hsl(30, 95%, 55%)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Upper Bound',
                    data: uppers,
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    backgroundColor: 'hsla(30, 95%, 55%, 0.1)',
                    borderWidth: 1,
                    fill: '+1',
                    pointRadius: 0
                },
                {
                    label: 'Lower Bound',
                    data: lowers,
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}

// 3. Burnout Alerts
async function loadAlerts() {
    const data = await fetchAPI('/burnout/');
    const list = document.getElementById('burnout-list');
    list.innerHTML = '';
    data.forEach(item => {
        list.innerHTML += `<li><span>${item.name}</span> <span style="color:#ff4b4b;">Score: ${item.risk_score.toFixed(0)}</span></li>`;
    });
}

async function triggerBurnoutScan() {
    await fetchAPI('/burnout/analyze', 'POST');
    loadAlerts();
}

// 4. Scheduling
async function loadSchedules() {
    const data = await fetchAPI('/schedules/');
    const list = document.getElementById('schedule-list');
    list.innerHTML = '';
    data.forEach(item => {
        list.innerHTML += `<li><span>${item.name}</span> <span>${item.schedule_date} | ${item.shift_start}-${item.shift_end}</span></li>`;
    });
}

async function optimizeSchedule() {
    const target_date = document.getElementById('schedule-date').value || new Date().toISOString().split('T')[0];
    const required_staff = parseInt(document.getElementById('required-staff').value);
    
    await fetchAPI('/schedules/optimize', 'POST', { target_date, required_staff });
    loadSchedules();
}

// 5. System
async function triggerEndOfMonth() {
    await fetchAPI('/system/end-of-month', 'POST');
    alert('End of Month Agents triggered successfully!');
    loadROI();
    loadAlerts();
}
