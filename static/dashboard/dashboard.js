// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing Dashboard');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Initialize Google Charts
    initializeGoogleCharts();
    
    // Add window resize listener for responsive charts
    window.addEventListener('resize', debounce(function() {
        redrawActiveChart();
    }, 250));
    
    // Test navigation functionality
    console.log('Testing navigation elements:');
    console.log('Dashboard page:', document.getElementById('dashboard-page'));
    console.log('Team page:', document.getElementById('team-page'));
    console.log('Projects page:', document.getElementById('projects-page'));
    console.log('Calendar page:', document.getElementById('calendar-page'));
    console.log('Documents page:', document.getElementById('documents-page'));
    console.log('Reports page:', document.getElementById('reports-page'));
    console.log('Settings page:', document.getElementById('settings-page'));
    
    // Test navigation click events
    const navLinks = document.querySelectorAll('.nav-link');
    console.log('Found nav links:', navLinks.length);
    navLinks.forEach((link, index) => {
        console.log(`Nav link ${index}:`, link.textContent.trim());
    });
});

function initializeDashboard() {
    // Add fade-in animation to main elements
    const mainElements = document.querySelectorAll('.sidebar, header, main');
    mainElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    console.log('Dashboard initialized successfully');
}

function initializeGoogleCharts() {
    console.log('Initializing Google Charts...');
    
    // Check if Google Charts is already loaded
    if (typeof google !== 'undefined' && google.charts) {
        console.log('Google Charts already available');
        google.charts.load('current', {'packages':['corechart']});
        google.charts.setOnLoadCallback(function() {
            console.log('Google Charts loaded successfully');
            // Show default chart for daily report
            showDefaultChartsForPage('team');
        });
    } else {
        console.log('Google Charts not available yet, waiting for script to load...');
        // Wait for Google Charts to load
        const checkGoogleCharts = setInterval(function() {
            if (typeof google !== 'undefined' && google.charts) {
                console.log('Google Charts now available');
                clearInterval(checkGoogleCharts);
                google.charts.load('current', {'packages':['corechart']});
                google.charts.setOnLoadCallback(function() {
                    console.log('Google Charts loaded successfully');
                    // Show default chart for daily report
                    showDefaultChartsForPage('team');
                });
            }
        }, 100);
        
        // Timeout after 10 seconds
        setTimeout(function() {
            clearInterval(checkGoogleCharts);
            console.log('Google Charts failed to load, showing default charts anyway');
            showDefaultChartsForPage('team');
        }, 10000);
    }
}

// Page navigation functionality
function showPage(pageId) {
    console.log('showPage called with:', pageId);
    
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Show selected page
    const targetPage = document.getElementById(pageId + '-page');
    if (targetPage) {
        targetPage.classList.remove('hidden');
        console.log('Showing page:', pageId + '-page');
    } else {
        console.error('Page not found:', pageId + '-page');
    }
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        link.classList.add('text-gray-300');
    });
    
    // Find the clicked link and make it active
    const clickedLink = event.target.closest('.nav-link');
    if (clickedLink) {
        clickedLink.classList.add('active');
        clickedLink.classList.remove('text-gray-300');
    }
    
    // Show default charts for the selected page
    showDefaultChartsForPage(pageId);
}

// Function to handle report option selection
function selectOption(optionId) {
    // Remove selected class from all report options in the same section
    const clickedOption = event.target.closest('.report-option');
    const reportSection = clickedOption.closest('.page-content');
    reportSection.querySelectorAll('.report-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selected class to clicked option
    clickedOption.classList.add('selected');
    
    // Check the corresponding radio button
    const radioButton = clickedOption.querySelector('input[type="radio"]');
    if (radioButton) {
        radioButton.checked = true;
    }
    
    // Show appropriate chart based on option and section
    const pageId = reportSection.id.replace('-page', '');
    switch(pageId) {
        case 'team':
            showDailyChart(optionId);
            break;
        case 'projects':
            showWeeklyChart(optionId);
            break;
        case 'calendar':
            showMonthlyChart(optionId);
            break;
        case 'documents':
            showQuarterlyChart(optionId);
            break;
        case 'reports':
            showAnnualChart(optionId);
            break;
    }
    
    console.log('Selected option:', optionId, 'in section:', pageId);
}

// Function to show default charts for all sections
function showDefaultChartsForPage(pageId) {
    console.log('showDefaultChartsForPage called with:', pageId);
    
    switch(pageId) {
        case 'team':
            console.log('Showing daily chart for team page');
            showDailyChart('today');
            break;
        case 'projects':
            console.log('Showing weekly chart for projects page');
            showWeeklyChart('this-week');
            break;
        case 'calendar':
            console.log('Showing monthly chart for calendar page');
            showMonthlyChart('this-month');
            break;
        case 'documents':
            console.log('Showing quarterly chart for documents page');
            showQuarterlyChart('this-quarter');
            break;
        case 'reports':
            console.log('Showing annual chart for reports page');
            showAnnualChart('this-year');
            break;
        default:
            console.log('No default chart for page:', pageId);
    }
}

// Daily Chart Functions
function showDailyChart(optionId) {
    console.log('showDailyChart called with:', optionId);
    
    // Hide all daily chart divs first
    const placeholder = document.getElementById('daily-chart-placeholder');
    const yesterdayChart = document.getElementById('yesterday-chart');
    const todayChart = document.getElementById('today-chart');
    const comparisonChart = document.getElementById('comparison-chart');
    
    if (placeholder) placeholder.classList.add('hidden');
    if (yesterdayChart) yesterdayChart.classList.add('hidden');
    if (todayChart) todayChart.classList.add('hidden');
    if (comparisonChart) comparisonChart.classList.add('hidden');
    
    console.log('Chart elements found:', {
        placeholder: !!placeholder,
        yesterdayChart: !!yesterdayChart,
        todayChart: !!todayChart,
        comparisonChart: !!comparisonChart
    });
    
    // Show selected chart
    if (optionId === 'yesterday') {
        if (yesterdayChart) {
            yesterdayChart.classList.remove('hidden');
            drawYesterdayChart();
        }
    } else if (optionId === 'today') {
        if (todayChart) {
            todayChart.classList.remove('hidden');
            drawTodayChart();
        }
    } else if (optionId === 'today-vs-yesterday') {
        if (comparisonChart) {
            comparisonChart.classList.remove('hidden');
            drawComparisonChart();
        }
    }
}

// Weekly Chart Functions
function showWeeklyChart(optionId) {
    // Hide all weekly chart divs first
    document.getElementById('weekly-chart-placeholder').classList.add('hidden');
    document.getElementById('this-week-chart').classList.add('hidden');
    document.getElementById('last-week-chart').classList.add('hidden');
    document.getElementById('this-week-vs-last-week-chart').classList.add('hidden');
    
    // Show selected chart
    if (optionId === 'this-week') {
        document.getElementById('this-week-chart').classList.remove('hidden');
        drawThisWeekChart();
    } else if (optionId === 'last-week') {
        document.getElementById('last-week-chart').classList.remove('hidden');
        drawLastWeekChart();
    } else if (optionId === 'this-week-vs-last-week') {
        document.getElementById('this-week-vs-last-week-chart').classList.remove('hidden');
        drawWeeklyComparisonChart();
    }
}

// Monthly Chart Functions
function showMonthlyChart(optionId) {
    // Hide all monthly chart divs first
    document.getElementById('monthly-chart-placeholder').classList.add('hidden');
    document.getElementById('this-month-chart').classList.add('hidden');
    document.getElementById('last-month-chart').classList.add('hidden');
    document.getElementById('this-month-vs-last-month-chart').classList.add('hidden');
    
    // Show selected chart
    if (optionId === 'this-month') {
        document.getElementById('this-month-chart').classList.remove('hidden');
        drawThisMonthChart();
    } else if (optionId === 'last-month') {
        document.getElementById('last-month-chart').classList.remove('hidden');
        drawLastMonthChart();
    } else if (optionId === 'this-month-vs-last-month') {
        document.getElementById('this-month-vs-last-month-chart').classList.remove('hidden');
        drawMonthlyComparisonChart();
    }
}

// Quarterly Chart Functions
function showQuarterlyChart(optionId) {
    // Hide all quarterly chart divs first
    document.getElementById('quarterly-chart-placeholder').classList.add('hidden');
    document.getElementById('this-quarter-chart').classList.add('hidden');
    document.getElementById('last-quarter-chart').classList.add('hidden');
    document.getElementById('this-quarter-vs-last-quarter-chart').classList.add('hidden');
    
    // Show selected chart
    if (optionId === 'this-quarter') {
        document.getElementById('this-quarter-chart').classList.remove('hidden');
        drawThisQuarterChart();
    } else if (optionId === 'last-quarter') {
        document.getElementById('last-quarter-chart').classList.remove('hidden');
        drawLastQuarterChart();
    } else if (optionId === 'this-quarter-vs-last-quarter') {
        document.getElementById('this-quarter-vs-last-quarter-chart').classList.remove('hidden');
        drawQuarterlyComparisonChart();
    }
}

// Annual Chart Functions
function showAnnualChart(optionId) {
    // Hide all annual chart divs first
    document.getElementById('annual-chart-placeholder').classList.add('hidden');
    document.getElementById('this-year-chart').classList.add('hidden');
    document.getElementById('last-year-chart').classList.add('hidden');
    document.getElementById('this-year-vs-last-year-chart').classList.add('hidden');
    
    // Show selected chart
    if (optionId === 'this-year') {
        document.getElementById('this-year-chart').classList.remove('hidden');
        drawThisYearChart();
    } else if (optionId === 'last-year') {
        document.getElementById('last-year-chart').classList.remove('hidden');
        drawLastYearChart();
    } else if (optionId === 'this-year-vs-last-year') {
        document.getElementById('this-year-vs-last-year-chart').classList.remove('hidden');
        drawAnnualComparisonChart();
    }
}

// Chart Drawing Functions
function drawYesterdayChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Category', 'Sales (VND)'],
        ['Đồ uống', 2500000],
        ['Món chính', 4500000],
        ['Món phụ', 1200000],
        ['Tráng miệng', 800000],
        ['Đồ ăn nhanh', 1800000]
    ]);

    const options = {
        title: 'Doanh số hôm qua theo danh mục',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#a855f7', '#c084fc', '#ddd6fe', '#e9d5ff'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('yesterday-chart'));
    chart.draw(data, options);
}

function drawTodayChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Hour', 'Sales (VND)'],
        ['6-9h', 800000],
        ['9-12h', 1200000],
        ['12-15h', 2800000],
        ['15-18h', 1500000],
        ['18-21h', 3200000],
        ['21-24h', 1800000]
    ]);

    const options = {
        title: 'Doanh số hôm nay theo giờ',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.LineChart(document.getElementById('today-chart'));
    chart.draw(data, options);
}

function drawComparisonChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Category', 'Hôm qua', 'Hôm nay'],
        ['Đồ uống', 2500000, 2800000],
        ['Món chính', 4500000, 5200000],
        ['Món phụ', 1200000, 1350000],
        ['Tráng miệng', 800000, 950000],
        ['Đồ ăn nhanh', 1800000, 2100000]
    ]);

    const options = {
        title: 'So sánh doanh số hôm qua vs hôm nay',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('comparison-chart'));
    chart.draw(data, options);
}

// Weekly Chart Drawing Functions
function drawThisWeekChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Day', 'Sales (VND)'],
        ['T2', 12000000],
        ['T3', 13500000],
        ['T4', 14200000],
        ['T5', 15800000],
        ['T6', 16800000],
        ['T7', 18500000],
        ['CN', 16500000]
    ]);

    const options = {
        title: 'Doanh số tuần này theo ngày',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.LineChart(document.getElementById('this-week-chart'));
    chart.draw(data, options);
}

function drawLastWeekChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Day', 'Sales (VND)'],
        ['T2', 11000000],
        ['T3', 12500000],
        ['T4', 13200000],
        ['T5', 14800000],
        ['T6', 15800000],
        ['T7', 17500000],
        ['CN', 15500000]
    ]);

    const options = {
        title: 'Doanh số tuần trước theo ngày',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.LineChart(document.getElementById('last-week-chart'));
    chart.draw(data, options);
}

function drawWeeklyComparisonChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Day', 'Tuần trước', 'Tuần này'],
        ['T2', 11000000, 12000000],
        ['T3', 12500000, 13500000],
        ['T4', 13200000, 14200000],
        ['T5', 14800000, 15800000],
        ['T6', 15800000, 16800000],
        ['T7', 17500000, 18500000],
        ['CN', 15500000, 16500000]
    ]);

    const options = {
        title: 'So sánh doanh số tuần trước vs tuần này',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-week-vs-last-week-chart'));
    chart.draw(data, options);
}

// Monthly Chart Drawing Functions
function drawThisMonthChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Week', 'Sales (VND)'],
        ['Tuần 1', 45000000],
        ['Tuần 2', 52000000],
        ['Tuần 3', 58000000],
        ['Tuần 4', 62000000]
    ]);

    const options = {
        title: 'Doanh số tháng này theo tuần',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-month-chart'));
    chart.draw(data, options);
}

function drawLastMonthChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Week', 'Sales (VND)'],
        ['Tuần 1', 42000000],
        ['Tuần 2', 48000000],
        ['Tuần 3', 54000000],
        ['Tuần 4', 58000000]
    ]);

    const options = {
        title: 'Doanh số tháng trước theo tuần',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('last-month-chart'));
    chart.draw(data, options);
}

function drawMonthlyComparisonChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Week', 'Tháng trước', 'Tháng này'],
        ['Tuần 1', 42000000, 45000000],
        ['Tuần 2', 48000000, 52000000],
        ['Tuần 3', 54000000, 58000000],
        ['Tuần 4', 58000000, 62000000]
    ]);

    const options = {
        title: 'So sánh doanh số tháng trước vs tháng này',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-month-vs-last-month-chart'));
    chart.draw(data, options);
}

// Quarterly Chart Drawing Functions
function drawThisQuarterChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Month', 'Sales (VND)'],
        ['Tháng 1', 180000000],
        ['Tháng 2', 195000000],
        ['Tháng 3', 210000000]
    ]);

    const options = {
        title: 'Doanh số quý này theo tháng',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-quarter-chart'));
    chart.draw(data, options);
}

function drawLastQuarterChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Month', 'Sales (VND)'],
        ['Tháng 10', 165000000],
        ['Tháng 11', 180000000],
        ['Tháng 12', 195000000]
    ]);

    const options = {
        title: 'Doanh số quý trước theo tháng',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('last-quarter-chart'));
    chart.draw(data, options);
}

function drawQuarterlyComparisonChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Month', 'Quý trước', 'Quý này'],
        ['Tháng 1', 165000000, 180000000],
        ['Tháng 2', 180000000, 195000000],
        ['Tháng 3', 195000000, 210000000]
    ]);

    const options = {
        title: 'So sánh doanh số quý trước vs quý này',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-quarter-vs-last-quarter-chart'));
    chart.draw(data, options);
}

// Annual Chart Drawing Functions
function drawThisYearChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Quarter', 'Sales (VND)'],
        ['Q1', 585000000],
        ['Q2', 620000000],
        ['Q3', 680000000],
        ['Q4', 720000000]
    ]);

    const options = {
        title: 'Doanh số năm này theo quý',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-year-chart'));
    chart.draw(data, options);
}

function drawLastYearChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Quarter', 'Sales (VND)'],
        ['Q1', 540000000],
        ['Q2', 580000000],
        ['Q3', 620000000],
        ['Q4', 680000000]
    ]);

    const options = {
        title: 'Doanh số năm trước theo quý',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('last-year-chart'));
    chart.draw(data, options);
}

function drawAnnualComparisonChart() {
    if (typeof google === 'undefined' || !google.visualization) return;
    
    const data = google.visualization.arrayToDataTable([
        ['Quarter', 'Năm trước', 'Năm này'],
        ['Q1', 540000000, 585000000],
        ['Q2', 580000000, 620000000],
        ['Q3', 620000000, 680000000],
        ['Q4', 680000000, 720000000]
    ]);

    const options = {
        title: 'So sánh doanh số năm trước vs năm này',
        titleTextStyle: {color: '#ffffff', fontSize: 18},
        backgroundColor: '#1e293b',
        colors: ['#8b5cf6', '#10b981'],
        legend: {textStyle: {color: '#ffffff'}},
        hAxis: {textStyle: {color: '#ffffff'}},
        vAxis: {textStyle: {color: '#ffffff'}},
        chartArea: {
            backgroundColor: '#1e293b',
            width: '85%',
            height: '70%',
            left: '10%',
            top: '15%'
        }
    };

    const chart = new google.visualization.ColumnChart(document.getElementById('this-year-vs-last-year-chart'));
    chart.draw(data, options);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function redrawActiveChart() {
    // Check daily report charts
    const yesterdayChart = document.getElementById('yesterday-chart');
    const todayChart = document.getElementById('today-chart');
    const comparisonChart = document.getElementById('comparison-chart');
    
    if (yesterdayChart && !yesterdayChart.classList.contains('hidden')) {
        drawYesterdayChart();
    } else if (todayChart && !todayChart.classList.contains('hidden')) {
        drawTodayChart();
    } else if (comparisonChart && !comparisonChart.classList.contains('hidden')) {
        drawComparisonChart();
    }
    
    // Check weekly report charts
    const thisWeekChart = document.getElementById('this-week-chart');
    const lastWeekChart = document.getElementById('last-week-chart');
    const weeklyComparisonChart = document.getElementById('this-week-vs-last-week-chart');
    
    if (thisWeekChart && !thisWeekChart.classList.contains('hidden')) {
        drawThisWeekChart();
    } else if (lastWeekChart && !lastWeekChart.classList.contains('hidden')) {
        drawLastWeekChart();
    } else if (weeklyComparisonChart && !weeklyComparisonChart.classList.contains('hidden')) {
        drawWeeklyComparisonChart();
    }
    
    // Check monthly report charts
    const thisMonthChart = document.getElementById('this-month-chart');
    const lastMonthChart = document.getElementById('last-month-chart');
    const monthlyComparisonChart = document.getElementById('this-month-vs-last-month-chart');
    
    if (thisMonthChart && !thisMonthChart.classList.contains('hidden')) {
        drawThisMonthChart();
    } else if (lastMonthChart && !lastMonthChart.classList.contains('hidden')) {
        drawLastMonthChart();
    } else if (monthlyComparisonChart && !monthlyComparisonChart.classList.contains('hidden')) {
        drawMonthlyComparisonChart();
    }
    
    // Check quarterly report charts
    const thisQuarterChart = document.getElementById('this-quarter-chart');
    const lastQuarterChart = document.getElementById('last-quarter-chart');
    const quarterlyComparisonChart = document.getElementById('this-quarter-vs-last-quarter-chart');
    
    if (thisQuarterChart && !thisQuarterChart.classList.contains('hidden')) {
        drawThisQuarterChart();
    } else if (lastQuarterChart && !lastQuarterChart.classList.contains('hidden')) {
        drawLastQuarterChart();
    } else if (quarterlyComparisonChart && !quarterlyComparisonChart.classList.contains('hidden')) {
        drawQuarterlyComparisonChart();
    }
    
    // Check annual report charts
    const thisYearChart = document.getElementById('this-year-chart');
    const lastYearChart = document.getElementById('last-year-chart');
    const annualComparisonChart = document.getElementById('this-year-vs-last-year-chart');
    
    if (thisYearChart && !thisYearChart.classList.contains('hidden')) {
        drawThisYearChart();
    } else if (lastYearChart && !lastYearChart.classList.contains('hidden')) {
        drawLastYearChart();
    } else if (annualComparisonChart && !annualComparisonChart.classList.contains('hidden')) {
        drawAnnualComparisonChart();
    }
}

// Console welcome message
console.log('%c🎨 Dashboard UI Ready!', 'color: #7c3aed; font-size: 16px; font-weight: bold;');
console.log('Available features:', {
    navigation: 'Click navigation items to switch sections',
    charts: 'All report sections with working charts',
    responsive: 'Resize window to see responsive behavior',
    interactions: 'Click report options to view different charts'
});

// Test function for debugging
window.testNavigation = function(pageId) {
    console.log('Testing navigation to:', pageId);
    showPage(pageId);
};
