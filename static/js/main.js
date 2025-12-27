// Timeline application JavaScript

const DEFAULT_START_YEAR = -5000000000;
const DEFAULT_END_YEAR = 2025;

let currentFigure = null;

// DOM elements
const startYearInput = document.getElementById('start-year');
const endYearInput = document.getElementById('end-year');
const updateBtn = document.getElementById('update-btn');
const resetBtn = document.getElementById('reset-btn');
const timelineContainer = document.getElementById('timeline-container');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTimeline(DEFAULT_START_YEAR, DEFAULT_END_YEAR);
    
    updateBtn.addEventListener('click', handleUpdate);
    resetBtn.addEventListener('click', handleReset);
    
    // Allow Enter key to trigger update
    startYearInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUpdate();
    });
    
    endYearInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUpdate();
    });
});

function handleUpdate() {
    const startYear = parseInt(startYearInput.value);
    const endYear = parseInt(endYearInput.value);
    
    // Validation
    if (isNaN(startYear) || isNaN(endYear)) {
        showError('Please enter valid numbers for start and end years.');
        return;
    }
    
    if (startYear >= endYear) {
        showError('Start year must be less than end year.');
        return;
    }
    
    loadTimeline(startYear, endYear);
}

function handleReset() {
    startYearInput.value = DEFAULT_START_YEAR;
    endYearInput.value = DEFAULT_END_YEAR;
    loadTimeline(DEFAULT_START_YEAR, DEFAULT_END_YEAR);
}

async function loadTimeline(startYear, endYear) {
    hideError();
    showLoading();
    
    try {
        console.log(`Loading timeline for range: ${startYear} to ${endYear}`);
        const response = await fetch(`/api/timeline?start_year=${startYear}&end_year=${endYear}`);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('API error:', error);
            throw new Error(error.error || 'Failed to load timeline');
        }
        
        const figureData = await response.json();
        console.log('Received figure data:', {
            dataLength: figureData.data?.length || 0,
            layout: figureData.layout?.title?.text || 'No title'
        });
        
        // Check if we have data
        if (!figureData.data || figureData.data.length === 0) {
            console.warn('No data traces in figure');
            showError('No data found for this time range. Try adjusting the year range.');
            hideLoading();
            return;
        }
        
        // Render Plotly figure
        Plotly.newPlot(timelineContainer, figureData.data, figureData.layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        });
        
        currentFigure = figureData;
        console.log('Timeline rendered successfully');
        hideLoading();
        
    } catch (error) {
        console.error('Error loading timeline:', error);
        showError(`Error: ${error.message}`);
        hideLoading();
    }
}

function showLoading() {
    loadingDiv.classList.remove('hidden');
    timelineContainer.style.opacity = '0.5';
}

function hideLoading() {
    loadingDiv.classList.add('hidden');
    timelineContainer.style.opacity = '1';
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    errorDiv.classList.add('hidden');
}

