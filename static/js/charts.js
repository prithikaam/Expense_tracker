/**
 * Expense Tracker System - Chart.js Rendering Module
 * Renders interactive Dashboard Visualizations
 */

function renderDashboardCharts(apiData) {
    // 1. Monthly Expense Trends (Line Chart)
    const trendCtx = document.getElementById('monthlyTrendChart');
    if (trendCtx && apiData.monthly_trend) {
        const labels = apiData.monthly_trend.map(item => item.month_year);
        const totals = apiData.monthly_trend.map(item => item.monthly_total);

        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Monthly Total (₹)',
                    data: totals,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#8b5cf6',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return ' Spend: ₹' + context.raw.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'Inter' },
                            callback: function(val) { return '₹' + val; }
                        }
                    }
                }
            }
        });
    }

    // 2. Category Breakdown (Doughnut Chart)
    const pieCtx = document.getElementById('categoryPieChart');
    if (pieCtx && apiData.category_breakdown) {
        const labels = apiData.category_breakdown.map(item => item.category_name);
        const values = apiData.category_breakdown.map(item => item.total_spent);
        const colors = apiData.category_breakdown.map(item => item.category_color || '#4f46e5');

        new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#1e293b',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            boxWidth: 12,
                            font: { family: 'Inter', size: 11 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ' ' + context.label + ': ₹' + context.raw.toFixed(2);
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Payment Method Distribution (Bar Chart)
    const payCtx = document.getElementById('paymentChart');
    if (payCtx && apiData.payment_breakdown) {
        const labels = apiData.payment_breakdown.map(item => item.payment_method);
        const values = apiData.payment_breakdown.map(item => item.total_amount);

        new Chart(payCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Spent (₹)',
                    data: values,
                    backgroundColor: [
                        '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#f8fafc', font: { family: 'Inter', weight: '500' } }
                    }
                }
            }
        });
    }
}
