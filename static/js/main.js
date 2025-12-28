// Timeline application JavaScript

const DEFAULT_START_YEAR = -5000000000;
const DEFAULT_END_YEAR = 2025;

let currentFigure = null;

// DOM elements
const startYearInput = document.getElementById('start-year');
const endYearInput = document.getElementById('end-year');
const updateBtn = document.getElementById('update-btn');
const resetBtn = document.getElementById('reset-btn');
const addEventBtn = document.getElementById('add-event-btn');
const manageEventsBtn = document.getElementById('manage-events-btn');
const timelineContainer = document.getElementById('timeline-container');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// Modal elements
const addEventModal = document.getElementById('add-event-modal');
const manageEventsModal = document.getElementById('manage-events-modal');
const addEventForm = document.getElementById('add-event-form');
const eventsListContainer = document.getElementById('events-list-container');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Ensure modals are hidden on page load
    if (addEventModal) hideModal(addEventModal);
    if (manageEventsModal) hideModal(manageEventsModal);
    
    // Load timeline
    loadTimeline(DEFAULT_START_YEAR, DEFAULT_END_YEAR);
    
    // Button handlers
    if (updateBtn) updateBtn.addEventListener('click', handleUpdate);
    if (resetBtn) resetBtn.addEventListener('click', handleReset);
    if (addEventBtn) addEventBtn.addEventListener('click', () => showModal(addEventModal));
    if (manageEventsBtn) {
        manageEventsBtn.addEventListener('click', () => {
            showModal(manageEventsModal);
            loadEventsList();
        });
    }
    
    // Modal close handlers
    const closeAddModal = document.getElementById('close-add-modal');
    const closeManageModal = document.getElementById('close-manage-modal');
    const cancelAddEvent = document.getElementById('cancel-add-event');
    
    if (closeAddModal) closeAddModal.addEventListener('click', () => hideModal(addEventModal));
    if (closeManageModal) closeManageModal.addEventListener('click', () => hideModal(manageEventsModal));
    if (cancelAddEvent) cancelAddEvent.addEventListener('click', () => hideModal(addEventModal));
    
    // Close modals when clicking outside
    if (addEventModal) {
        addEventModal.addEventListener('click', (e) => {
            if (e.target === addEventModal) hideModal(addEventModal);
        });
    }
    if (manageEventsModal) {
        manageEventsModal.addEventListener('click', (e) => {
            if (e.target === manageEventsModal) hideModal(manageEventsModal);
        });
    }
    
    // Close modals with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (addEventModal && !addEventModal.classList.contains('hidden')) {
                hideModal(addEventModal);
            }
            if (manageEventsModal && !manageEventsModal.classList.contains('hidden')) {
                hideModal(manageEventsModal);
            }
        }
    });
    
    // Form submission
    if (addEventForm) addEventForm.addEventListener('submit', handleAddEvent);
    
    // Allow Enter key to trigger update
    if (startYearInput) {
        startYearInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleUpdate();
        });
    }
    
    if (endYearInput) {
        endYearInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleUpdate();
        });
    }
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

// Modal functions
function showModal(modal) {
    if (modal) {
        modal.classList.remove('hidden');
        // Prevent body scroll when modal is open
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modal) {
    if (modal) {
        modal.classList.add('hidden');
        // Restore body scroll
        document.body.style.overflow = '';
    }
}

// Make hideModal available globally for error handlers
window.hideModal = hideModal;

// Add Event functionality
async function handleAddEvent(e) {
    e.preventDefault();
    
    const eventData = {
        title: document.getElementById('event-title').value.trim(),
        category: document.getElementById('event-category').value,
        continent: document.getElementById('event-continent').value.trim() || 'Global',
        start_year: parseInt(document.getElementById('event-start-year').value),
        end_year: document.getElementById('event-end-year').value 
            ? parseInt(document.getElementById('event-end-year').value)
            : undefined,
        description: document.getElementById('event-description').value.trim()
    };
    
    // Validation
    if (!eventData.title || !eventData.category || isNaN(eventData.start_year)) {
        showError('Please fill in all required fields (Title, Category, Start Year)');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/events', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to add event');
        }
        
        // Success - reload timeline and close modal
        hideModal(addEventModal);
        addEventForm.reset();
        hideError();
        
        // Reload timeline with current year range
        const currentStart = parseInt(startYearInput.value);
        const currentEnd = parseInt(endYearInput.value);
        await loadTimeline(currentStart, currentEnd);
        
        // Show success message
        showSuccess('Event added successfully!');
        
    } catch (error) {
        console.error('Error adding event:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Load events list for management
async function loadEventsList() {
    try {
        eventsListContainer.innerHTML = '<div class="loading">Loading events...</div>';
        
        const currentStart = parseInt(startYearInput.value);
        const currentEnd = parseInt(endYearInput.value);
        
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch(`/api/events?start_year=${currentStart}&end_year=${currentEnd}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}: Failed to load events`);
        }
        
        const result = await response.json();
        
        if (result.count === 0) {
            eventsListContainer.innerHTML = '<div class="empty-state">No events found in the current time range.</div>';
            return;
        }
        
        // Render events list
        const eventsHtml = result.data.map(event => `
            <div class="event-card">
                <div class="event-info">
                    <div class="event-title">${escapeHtml(event.title || 'Untitled')}</div>
                    <div class="event-details">
                        <strong>Category:</strong> ${escapeHtml(event.category || 'N/A')} | 
                        <strong>Continent:</strong> ${escapeHtml(event.continent || 'N/A')}
                    </div>
                    <div class="event-details">
                        <strong>Years:</strong> ${formatYear(event.start_year)} - ${formatYear(event.end_year || event.start_year)}
                    </div>
                    ${event.description ? `<div class="event-description">${escapeHtml(event.description)}</div>` : ''}
                </div>
                <button class="btn-delete" onclick="deleteEvent('${event.id}')">Delete</button>
            </div>
        `).join('');
        
        eventsListContainer.innerHTML = `<div class="events-list">${eventsHtml}</div>`;
        
    } catch (error) {
        console.error('Error loading events:', error);
        let errorMessage = 'Error loading events: ';
        if (error.name === 'AbortError') {
            errorMessage += 'Request timed out. The database may not be connected.';
        } else {
            errorMessage += error.message || 'Unknown error occurred';
        }
        eventsListContainer.innerHTML = `
            <div class="error">
                ${errorMessage}
                <br><br>
                <button class="btn-secondary" onclick="loadEventsList()">Retry</button>
                <button class="btn-secondary" onclick="hideModal(manageEventsModal)">Close</button>
            </div>
        `;
    }
}

// Delete event
async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`/api/events/${eventId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to delete event');
        }
        
        // Success - reload events list and timeline
        await loadEventsList();
        
        const currentStart = parseInt(startYearInput.value);
        const currentEnd = parseInt(endYearInput.value);
        await loadTimeline(currentStart, currentEnd);
        
        showSuccess('Event deleted successfully!');
        
    } catch (error) {
        console.error('Error deleting event:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Helper functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatYear(year) {
    if (year === null || year === undefined || isNaN(year)) return 'N/A';
    return year.toLocaleString();
}

function showSuccess(message) {
    // Create a temporary success message
    const successDiv = document.createElement('div');
    successDiv.className = 'error';
    successDiv.style.background = 'rgba(40, 167, 69, 0.2)';
    successDiv.style.borderColor = 'rgba(40, 167, 69, 0.5)';
    successDiv.style.color = '#6cff87';
    successDiv.textContent = message;
    errorDiv.parentNode.insertBefore(successDiv, errorDiv.nextSibling);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Make deleteEvent available globally for onclick handlers
window.deleteEvent = deleteEvent;

