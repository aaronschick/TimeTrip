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
const eventSearchInput = document.getElementById('event-search');
const searchResultsDiv = document.getElementById('search-results');

// Modal elements
const addEventModal = document.getElementById('add-event-modal');
const manageEventsModal = document.getElementById('manage-events-modal');
const importCsvModal = document.getElementById('import-csv-modal');
const addEventForm = document.getElementById('add-event-form');
const eventsListContainer = document.getElementById('events-list-container');
const importStatusContainer = document.getElementById('import-status-info');
const importResultDiv = document.getElementById('import-result');
const clustersToggleBtn = document.getElementById('clusters-toggle-btn');

// Clustering state
let clusteringEnabled = true;
let clusterInfo = {};  // Store cluster info from API response

// Map selection functions
function toggleMapSelectionMode() {
    window.appState.mapSelectionMode = !window.appState.mapSelectionMode;
    const filterControls = document.getElementById('map-filter-controls');
    if (filterControls) {
        if (window.appState.mapSelectionMode) {
            filterControls.classList.remove('hidden');
        } else {
            filterControls.classList.add('hidden');
        }
    }
    // Refresh Earth view to show/hide selection mode UI
    const currentEvent = window.appState.selectedEvent;
    if (currentEvent && currentEvent.lat && currentEvent.lon) {
        centerGlobeOnLocation(currentEvent.lat, currentEvent.lon, currentEvent.location_label || currentEvent.continent || 'Location');
    } else {
        updateEarthView(currentEvent?.continent || 'Global');
    }
}

function applyMapFilter() {
    const latInput = document.getElementById('filter-lat');
    const lonInput = document.getElementById('filter-lon');
    const radiusInput = document.getElementById('filter-radius');
    
    if (!latInput || !lonInput) return;
    
    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lonInput.value);
    const radius = radiusInput ? parseFloat(radiusInput.value) || 500 : 500;
    
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        showError('Please enter valid latitude (-90 to 90) and longitude (-180 to 180)');
        return;
    }
    
    window.appState.mapFilter = {
        type: 'point',
        lat: lat,
        lon: lon,
        radius: radius
    };
    
    // Reload timeline with filter
    const currentStart = parseInt(startYearInput.value);
    const currentEnd = parseInt(endYearInput.value);
    loadTimeline(currentStart, currentEnd);
    
    // Center globe on filter location
    centerGlobeOnLocation(lat, lon, `Filter: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
}

function clearMapFilter() {
    window.appState.mapFilter = null;
    const filterControls = document.getElementById('map-filter-controls');
    if (filterControls) {
        filterControls.classList.add('hidden');
    }
    window.appState.mapSelectionMode = false;
    
    // Clear input fields
    const latInput = document.getElementById('filter-lat');
    const lonInput = document.getElementById('filter-lon');
    if (latInput) latInput.value = '';
    if (lonInput) lonInput.value = '';
    
    // Reload timeline without filter
    const currentStart = parseInt(startYearInput.value);
    const currentEnd = parseInt(endYearInput.value);
    loadTimeline(currentStart, currentEnd);
    
    // Refresh Earth view
    const currentEvent = window.appState.selectedEvent;
    if (currentEvent && currentEvent.lat && currentEvent.lon) {
        centerGlobeOnLocation(currentEvent.lat, currentEvent.lon, currentEvent.location_label || currentEvent.continent || 'Location');
    } else {
        updateEarthView(currentEvent?.continent || 'Global');
    }
}

// Make functions globally available
window.toggleMapSelectionMode = toggleMapSelectionMode;
window.clearMapFilter = clearMapFilter;
window.applyMapFilter = applyMapFilter;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Observatory Mode
    initStarfield('starfield');
    initBackdrops();
    
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
    const importCsvBtnHeader = document.getElementById('import-csv-btn-header');
    if (importCsvBtnHeader) {
        importCsvBtnHeader.addEventListener('click', () => {
            showModal(importCsvModal);
            checkImportStatus();
        });
    }
    
    // Modal close handlers
    const closeAddModal = document.getElementById('close-add-modal');
    const closeManageModal = document.getElementById('close-manage-modal');
    const closeImportModal = document.getElementById('close-import-modal');
    const cancelAddEvent = document.getElementById('cancel-add-event');
    const cancelImport = document.getElementById('cancel-import');
    
    if (closeAddModal) closeAddModal.addEventListener('click', () => hideModal(addEventModal));
    if (closeManageModal) closeManageModal.addEventListener('click', () => hideModal(manageEventsModal));
    if (closeImportModal) closeImportModal.addEventListener('click', () => hideModal(importCsvModal));
    if (cancelAddEvent) cancelAddEvent.addEventListener('click', () => hideModal(addEventModal));
    if (cancelImport) cancelImport.addEventListener('click', () => hideModal(importCsvModal));
    
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
    if (importCsvModal) {
        importCsvModal.addEventListener('click', (e) => {
            if (e.target === importCsvModal) hideModal(importCsvModal);
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
            if (importCsvModal && !importCsvModal.classList.contains('hidden')) {
                hideModal(importCsvModal);
            }
        }
    });
    
    // Import CSV handlers
    const importCsvBtn = document.getElementById('import-csv-btn');
    const importCsvClearBtn = document.getElementById('import-csv-clear-btn');
    if (importCsvBtn) importCsvBtn.addEventListener('click', () => importCsv(false));
    if (importCsvClearBtn) importCsvClearBtn.addEventListener('click', () => importCsv(true));
    
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
    
    // Event search functionality
    if (eventSearchInput) {
        eventSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                hideSearchResults();
                return;
            }
            
            searchTimeout = setTimeout(() => {
                searchEvents(query);
            }, 300); // Debounce search
        });
        
        eventSearchInput.addEventListener('keydown', (e) => {
            if (!searchResultsDiv.classList.contains('hidden') && currentSearchResults.length > 0) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    selectedSearchIndex = Math.min(selectedSearchIndex + 1, currentSearchResults.length - 1);
                    updateSearchSelection();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    selectedSearchIndex = Math.max(selectedSearchIndex - 1, -1);
                    updateSearchSelection();
                } else if (e.key === 'Enter' && selectedSearchIndex >= 0) {
                    e.preventDefault();
                    selectEvent(currentSearchResults[selectedSearchIndex]);
                } else if (e.key === 'Escape') {
                    hideSearchResults();
                }
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (eventSearchInput && !eventSearchInput.contains(e.target) && 
                searchResultsDiv && !searchResultsDiv.contains(e.target)) {
                hideSearchResults();
            }
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

function toggleClustering() {
    clusteringEnabled = !clusteringEnabled;
    if (clustersToggleBtn) {
        clustersToggleBtn.textContent = `Clusters: ${clusteringEnabled ? 'On' : 'Off'}`;
        clustersToggleBtn.classList.toggle('btn-secondary', clusteringEnabled);
        clustersToggleBtn.classList.toggle('btn-warning', !clusteringEnabled);
    }
    
    // Reload timeline with new clustering setting
    const currentStart = parseInt(startYearInput.value);
    const currentEnd = parseInt(endYearInput.value);
    loadTimeline(currentStart, currentEnd);
}

async function loadTimeline(startYear, endYear) {
    hideError();
    showLoading();
    
    // Clear any existing highlight when loading new timeline
    clearEventHighlight();
    
    try {
        console.log(`Loading timeline for range: ${startYear} to ${endYear}`);
        
        // Build URL with location filter and clustering option
        let url = `/api/timeline?start_year=${startYear}&end_year=${endYear}&enable_clustering=${clusteringEnabled}`;
        if (window.appState.mapFilter && window.appState.mapFilter.type === 'point') {
            url += `&filter_lat=${window.appState.mapFilter.lat}&filter_lon=${window.appState.mapFilter.lon}`;
            if (window.appState.mapFilter.radius) {
                url += `&filter_radius=${window.appState.mapFilter.radius}`;
            }
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('API error:', error);
            throw new Error(error.error || 'Failed to load timeline');
        }
        
        const figureData = await response.json();
        console.log('Received figure data:', {
            dataLength: figureData.data?.length || 0,
            layout: figureData.layout?.title?.text || 'No title',
            metadata: figureData._metadata || 'No metadata'
        });
        
        // Store cluster info for expansion
        if (figureData._metadata && figureData._metadata.cluster_info) {
            clusterInfo = figureData._metadata.cluster_info;
        } else {
            clusterInfo = {};
        }
        
        // Check if we have metadata indicating no data
        if (figureData._metadata && figureData._metadata.filtered_events === 0) {
            console.warn('No events in filtered range');
            showError(`No events found in the time range ${startYear.toLocaleString()} to ${endYear.toLocaleString()}. Try adjusting the year range or check if events are in the database.`);
            hideLoading();
            return;
        }
        
        // Check if we have data traces
        if (!figureData.data || figureData.data.length === 0) {
            console.warn('No data traces in figure');
            // Check if it's an empty figure with annotation
            if (figureData.layout && figureData.layout.annotations) {
                // This is an intentional empty figure, render it
                Plotly.newPlot(timelineContainer, figureData.data || [], figureData.layout, {
                    responsive: true,
                    displayModeBar: true,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                });
                hideLoading();
                return;
            }
            showError('No data found for this time range. Try adjusting the year range.');
            hideLoading();
            return;
        }
        
        // Render Plotly figure
        Plotly.newPlot(timelineContainer, figureData.data, figureData.layout, {
            responsive: true,
            displayModeBar: 'hover',
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        });
        
        currentFigure = figureData;
        console.log('Timeline rendered successfully');
        hideLoading();
        
        // Wire up Plotly events for Observatory Mode
        wireUpPlotlyEvents();
        
        // Set initial backdrop based on current year range
        const midYear = (startYear + endYear) / 2;
        if (typeof setBackdropForYear === 'function') {
            setBackdropForYear(midYear);
        }
        
        // If an event was selected from search, highlight it after a short delay
        if (window.selectedEventId && window.selectedEventData) {
            setTimeout(() => {
                highlightEventOnTimeline(window.selectedEventId, window.selectedEventData);
                // Clear the selection flag after highlighting
                delete window.selectedEventId;
            }, 800); // Delay to ensure Plotly is fully rendered and data is available
        }
        
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
    
    // Add location fields if provided
    const latInput = document.getElementById('event-lat');
    const lonInput = document.getElementById('event-lon');
    const locationLabelInput = document.getElementById('event-location-label');
    const geometryInput = document.getElementById('event-geometry');
    const locationConfidenceInput = document.getElementById('event-location-confidence');
    
    if (latInput && latInput.value.trim()) {
        eventData.lat = parseFloat(latInput.value.trim());
    }
    if (lonInput && lonInput.value.trim()) {
        eventData.lon = parseFloat(lonInput.value.trim());
    }
    if (locationLabelInput && locationLabelInput.value.trim()) {
        eventData.location_label = locationLabelInput.value.trim();
    }
    if (geometryInput && geometryInput.value.trim()) {
        eventData.geometry = geometryInput.value.trim();
    }
    if (locationConfidenceInput) {
        eventData.location_confidence = locationConfidenceInput.value;
    }
    
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

// Event search functionality
let searchTimeout;
let selectedSearchIndex = -1;
let currentSearchResults = [];

async function searchEvents(query) {
    try {
        const response = await fetch(`/api/events/search?q=${encodeURIComponent(query)}&limit=10`);
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const result = await response.json();
        currentSearchResults = result.data || [];
        selectedSearchIndex = -1;
        
        displaySearchResults(currentSearchResults);
        
    } catch (error) {
        console.error('Error searching events:', error);
        searchResultsDiv.innerHTML = '<div class="search-no-results">Error searching events</div>';
        showSearchResults();
    }
}

function displaySearchResults(results) {
    if (!searchResultsDiv) return;
    
    if (results.length === 0) {
        searchResultsDiv.innerHTML = '<div class="search-no-results">No events found</div>';
        showSearchResults();
        return;
    }
    
    const html = results.map((event, index) => {
        const category = escapeHtml(event.category || 'N/A');
        const continent = escapeHtml(event.continent || 'N/A');
        const year = formatYear(event.start_year);
        
        return `
            <div class="search-result-item" data-index="${index}" data-event-id="${event.id}" 
                 data-start-year="${event.start_year}" data-end-year="${event.end_year || event.start_year}">
                <div class="search-result-title">${escapeHtml(event.title || 'Untitled')}</div>
                <div class="search-result-details">
                    <span class="search-result-category">${category}</span>
                    <span>${continent}</span>
                    <span style="margin-left: 8px;">${year}</span>
                </div>
            </div>
        `;
    }).join('');
    
    searchResultsDiv.innerHTML = html;
    showSearchResults();
    
    // Add click handlers
    searchResultsDiv.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            selectEvent(currentSearchResults[index]);
        });
    });
}

function updateSearchSelection() {
    if (!searchResultsDiv) return;
    
    const items = searchResultsDiv.querySelectorAll('.search-result-item');
    items.forEach((item, index) => {
        if (index === selectedSearchIndex) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        } else {
            item.classList.remove('selected');
        }
    });
}

function selectEvent(event) {
    if (!event) return;
    
    // Hide search results
    hideSearchResults();
    
    // Clear search input
    if (eventSearchInput) {
        eventSearchInput.value = '';
    }
    
    // Calculate year range to center on this event
    const eventStartYear = event.start_year;
    const eventEndYear = event.end_year || event.start_year;
    
    // Set a range around the event (show 10% of timeline on each side, or minimum 1000 years)
    const yearSpan = Math.max(eventEndYear - eventStartYear, 1000);
    const padding = Math.max(yearSpan * 0.1, 1000);
    
    const newStartYear = Math.floor(eventStartYear - padding);
    const newEndYear = Math.ceil(eventEndYear + padding);
    
    // Update year inputs
    if (startYearInput) startYearInput.value = newStartYear;
    if (endYearInput) endYearInput.value = newEndYear;
    
    // Store event ID for highlighting after timeline loads
    window.selectedEventId = event.id;
    window.selectedEventData = event;
    
    // Reload timeline with new range
    loadTimeline(newStartYear, newEndYear).then(() => {
        // After timeline loads, highlight the event
        highlightEventOnTimeline(event.id, event);
        console.log(`Centered timeline on event: ${event.title} (${eventStartYear} - ${eventEndYear})`);
    });
}

function showSearchResults() {
    if (searchResultsDiv) {
        searchResultsDiv.classList.remove('hidden');
    }
}

function hideSearchResults() {
    if (searchResultsDiv) {
        searchResultsDiv.classList.add('hidden');
    }
    selectedSearchIndex = -1;
    currentSearchResults = [];
}

// Observatory Mode: Wire up Plotly events
function wireUpPlotlyEvents() {
    if (!timelineContainer) return;
    
    const graphDiv = timelineContainer;
    
    // Handle relayout (pan/zoom) - update backdrop
    graphDiv.on('plotly_relayout', (eventData) => {
        updateBackdropFromPlotly(eventData);
    });
    
    // Handle click - show event details
    graphDiv.on('plotly_click', (data) => {
        handlePlotlyClick(data);
    });
    
    // Add fluid scrolling with mouse/trackpad
    enableFluidScrolling(graphDiv);
}

// Update backdrop based on visible time range
function updateBackdropFromPlotly(eventData) {
    if (!timelineContainer) return;
    
    const graphDiv = timelineContainer;
    let startYear, endYear;
    
    // Try to get range from relayout event data
    if (eventData && eventData['xaxis.range[0]'] !== undefined) {
        startYear = eventData['xaxis.range[0]'];
        endYear = eventData['xaxis.range[1]'];
    } else if (graphDiv.layout && graphDiv.layout.xaxis && graphDiv.layout.xaxis.range) {
        // Fallback to layout
        startYear = graphDiv.layout.xaxis.range[0];
        endYear = graphDiv.layout.xaxis.range[1];
    } else {
        // Fallback to current input values
        startYear = parseInt(startYearInput.value);
        endYear = parseInt(endYearInput.value);
    }
    
    // Calculate midpoint year
    const midYear = (startYear + endYear) / 2;
    
    // Update backdrop
    if (typeof setBackdropForYear === 'function') {
        setBackdropForYear(midYear);
    }
}

// Handle Plotly point click - populate event details or expand cluster
function handlePlotlyClick(data) {
    if (!data || !data.points || data.points.length === 0) return;
    
    const point = data.points[0];
    const customdata = point.customdata;
    
    if (!customdata) {
        console.warn('No customdata found for clicked point');
        return;
    }
    
    // Check if this is a cluster (customdata indices: 14=is_cluster, 15=cluster_id)
    const is_cluster = customdata[14] === true || customdata[14] === 'True';
    const cluster_id = customdata[15];
    
    if (is_cluster && cluster_id && clusterInfo[cluster_id]) {
        // Expand cluster by zooming into its time range
        expandCluster(cluster_id);
    } else {
        // Regular event - show details
        clearEventHighlight();
        populateEventDetails(customdata);
    }
}

// Expand cluster by zooming into its time range
function expandCluster(clusterId) {
    const cluster = clusterInfo[clusterId];
    if (!cluster) {
        console.warn(`Cluster ${clusterId} not found`);
        return;
    }
    
    // Calculate zoom range with some padding
    const bucketRange = cluster.bucket_end - cluster.bucket_start;
    const padding = bucketRange * 0.1; // 10% padding
    const newStart = Math.floor(cluster.bucket_start - padding);
    const newEnd = Math.ceil(cluster.bucket_end + padding);
    
    // Update year inputs
    if (startYearInput) startYearInput.value = newStart;
    if (endYearInput) endYearInput.value = newEnd;
    
    // Temporarily disable clustering for this zoom level
    // (will re-enable if user zooms back out)
    const wasClusteringEnabled = clusteringEnabled;
    clusteringEnabled = false;
    
    // Reload timeline zoomed into cluster range
    loadTimeline(newStart, newEnd).then(() => {
        // Show cluster preview in sidebar
        showClusterPreview(cluster);
        
        // Re-enable clustering after a delay (user can toggle manually)
        setTimeout(() => {
            if (wasClusteringEnabled) {
                clusteringEnabled = true;
                if (clustersToggleBtn) {
                    clustersToggleBtn.textContent = 'Clusters: On';
                }
            }
        }, 2000);
    });
}

// Show cluster preview in event details sidebar
function showClusterPreview(cluster) {
    const detailsContainer = document.getElementById('event-details-content');
    if (!detailsContainer) return;
    
    const events = cluster.events || [];
    const previewCount = Math.min(10, events.length);
    const remainingCount = events.length - previewCount;
    
    const eventsList = events.slice(0, previewCount).map(event => {
        const year = event.start_year || event.end_year || 'N/A';
        return `<div style="padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <strong>${escapeHtml(event.title || 'Untitled')}</strong><br>
            <small style="opacity: 0.7;">${formatYear(year)} | ${escapeHtml(event.category || 'N/A')}</small>
        </div>`;
    }).join('');
    
    const html = `
        <div class="event-detail-item">
            <div class="event-detail-label">Cluster</div>
            <div class="event-detail-value">
                <strong>${cluster.event_count} events</strong><br>
                <small style="opacity: 0.7;">${formatYear(cluster.bucket_start)} - ${formatYear(cluster.bucket_end)}</small>
            </div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Category</div>
            <div class="event-detail-value">${escapeHtml(cluster.category || 'N/A')}</div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Events in Cluster</div>
            <div class="event-detail-value" style="max-height: 300px; overflow-y: auto;">
                ${eventsList}
                ${remainingCount > 0 ? `<div style="padding: 10px 0; text-align: center; opacity: 0.7;">
                    <em>... and ${remainingCount} more event${remainingCount > 1 ? 's' : ''}</em>
                </div>` : ''}
            </div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Status</div>
            <div class="event-detail-value">
                <small style="opacity: 0.7;">Timeline zoomed to cluster range. Clustering disabled for this view.</small>
            </div>
        </div>
    `;
    
    detailsContainer.innerHTML = html;
    
    // Update Earth view if cluster has location info
    if (cluster.continent) {
        updateEarthView(cluster.continent);
    }
}

// Continent to coordinates mapping for Google Earth
// Zoom levels: 1 = world, 2 = continent, 3 = country, 4 = region, 5 = city
// Using lower zoom values for better continent-level view
const CONTINENT_COORDINATES = {
    'Global': { lat: 0, lng: 0, zoom: 1 },
    'Africa': { lat: 8.7832, lng: 34.5085, zoom: 2 },
    'Asia': { lat: 34.0479, lng: 100.6197, zoom: 2 },
    'Europe': { lat: 54.5260, lng: 15.2551, zoom: 3 },
    'North America': { lat: 54.5260, lng: -105.2551, zoom: 2 },
    'South America': { lat: -14.2350, lng: -51.9253, zoom: 2 },
    'Australia': { lat: -25.2744, lng: 133.7751, zoom: 3 },
    'Oceania': { lat: -8.7832, lng: 124.5085, zoom: 2 },
    'Antarctica': { lat: -75.2509, lng: -0.0713, zoom: 2 },
    'Americas': { lat: 20.0, lng: -80.0, zoom: 2 },
    'Middle East': { lat: 29.2985, lng: 42.5503, zoom: 3 },
    'Mediterranean': { lat: 38.0, lng: 20.0, zoom: 3 },
    'Eurasia': { lat: 50.0, lng: 50.0, zoom: 1 }
};

// Populate event details sidebar
function populateEventDetails(eventData) {
    const detailsContainer = document.getElementById('event-details-content');
    if (!detailsContainer) return;
    
    // Parse customdata (it might be an array or object)
    let event = eventData;
    if (Array.isArray(eventData)) {
        // If it's an array, assume it's [id, title, category, continent, start_year, end_year, start_date, end_date, description, lat, lon, location_label, geometry, location_confidence]
        event = {
            id: eventData[0] || null,
            title: eventData[1] || 'Unknown',
            category: eventData[2] || 'N/A',
            continent: eventData[3] || 'N/A',
            start_year: eventData[4] || null,
            end_year: eventData[5] || null,
            start_date: eventData[6] || null,
            end_date: eventData[7] || null,
            description: eventData[8] || null,
            lat: eventData[9] !== undefined && eventData[9] !== null ? eventData[9] : null,
            lon: eventData[10] !== undefined && eventData[10] !== null ? eventData[10] : null,
            location_label: eventData[11] || null,
            geometry: eventData[12] || null,
            location_confidence: eventData[13] || 'exact'
        };
    }
    
    // Build HTML
    const html = `
        <div class="event-detail-item">
            <div class="event-detail-label">Title</div>
            <div class="event-detail-value">${escapeHtml(event.title || 'Unknown')}</div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Category</div>
            <div class="event-detail-value">${escapeHtml(event.category || 'N/A')}</div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Continent</div>
            <div class="event-detail-value">${escapeHtml(event.continent || 'N/A')}</div>
        </div>
        <div class="event-detail-item">
            <div class="event-detail-label">Time Period</div>
            <div class="event-detail-value">
                ${formatYear(event.start_year)} - ${formatYear(event.end_year || event.start_year)}
                ${event.start_date ? `<br><small style="opacity: 0.7;">${escapeHtml(event.start_date)}</small>` : ''}
                ${event.end_date && event.end_date !== event.start_date ? `<br><small style="opacity: 0.7;">to ${escapeHtml(event.end_date)}</small>` : ''}
            </div>
        </div>
        ${event.description ? `
        <div class="event-detail-item">
            <div class="event-detail-label">Description</div>
            <div class="event-detail-description">${escapeHtml(event.description)}</div>
        </div>
        ` : ''}
        ${(event.lat !== null && event.lat !== undefined) || (event.lon !== null && event.lon !== undefined) || event.location_label ? `
        <div class="event-detail-item">
            <div class="event-detail-label">Location</div>
            <div class="event-detail-value">
                ${event.location_label ? `<strong>${escapeHtml(event.location_label)}</strong><br>` : ''}
                ${(event.lat !== null && event.lat !== undefined) && (event.lon !== null && event.lon !== undefined) 
                    ? `${event.lat.toFixed(4)}, ${event.lon.toFixed(4)}` 
                    : ''}
                ${event.location_confidence && event.location_confidence !== 'exact' 
                    ? `<br><small style="opacity: 0.7;">Confidence: ${escapeHtml(event.location_confidence)}</small>` 
                    : ''}
            </div>
        </div>
        ` : ''}
    `;
    
    detailsContainer.innerHTML = html;
    
    // Store selected event in app state
    window.appState.selectedEvent = event;
    
    // Update Earth view - use event location if available, otherwise use continent
    if (event.lat !== null && event.lat !== undefined && event.lon !== null && event.lon !== undefined) {
        // Center on event location
        centerGlobeOnLocation(event.lat, event.lon, event.location_label || event.continent || 'Global');
    } else {
        // Fall back to continent
        updateEarthView(event.continent || 'Global');
    }
}

// Center globe on specific location (lat/lon)
function centerGlobeOnLocation(lat, lon, label) {
    const earthContainer = document.getElementById('earth-container');
    if (!earthContainer) return;
    
    // Use a closer zoom level for specific locations
    const zoom = 6; // City/region level
    
    const coords = { lat, lng: lon, zoom };
    createGlobeVisualization(earthContainer, label || 'Location', coords, true);
}

// Update Earth view based on continent
function updateEarthView(continent) {
    const earthContainer = document.getElementById('earth-container');
    if (!earthContainer) return;
    
    // Normalize continent name (handle variations)
    const normalizedContinent = normalizeContinentName(continent);
    const coords = CONTINENT_COORDINATES[normalizedContinent] || CONTINENT_COORDINATES['Global'];
    
    // Create or update the Earth visualization
    createGlobeVisualization(earthContainer, normalizedContinent, coords, false);
}

// Normalize continent name to match our coordinate map
function normalizeContinentName(continent) {
    if (!continent) return 'Global';
    
    const normalized = continent.trim();
    
    // Handle variations
    const mapping = {
        'africa': 'Africa',
        'asia': 'Asia',
        'europe': 'Europe',
        'north america': 'North America',
        'south america': 'South America',
        'australia': 'Australia',
        'oceania': 'Oceania',
        'antarctica': 'Antarctica',
        'americas': 'Americas',
        'middle east': 'Middle East',
        'mediterranean': 'Mediterranean',
        'eurasia': 'Eurasia',
        'global': 'Global'
    };
    
    return mapping[normalized.toLowerCase()] || normalized;
}

// App state for two-way linking
window.appState = {
    selectedEvent: null,
    mapFilter: null, // { type: 'point'|'region', lat, lon, radius?, geometry? }
    mapSelectionMode: false
};

// Create a simple globe visualization (no heavy dependencies)
function createGlobeVisualization(container, continent, coords, isSpecificLocation = false) {
    // Clear container
    container.innerHTML = '';
    
    // Create Google Maps embed with satellite/terrain view
    // Note: Google Maps embed requires API key for full functionality
    // We'll use a direct Google Maps URL that works without API key
    // and provide a link to Google Earth for full 3D experience
    
    const earthLink = `https://earth.google.com/web/@${coords.lat},${coords.lng},${coords.zoom}a,0y,0h,0t,0r`;
    const mapsLink = `https://www.google.com/maps/@${coords.lat},${coords.lng},${coords.zoom}z/data=!3m1!1e3`;
    
    // Create Google Maps embed iframe
    // Using Google Maps embed URL format (works for viewing without API key in some cases)
    // If embed doesn't work, we'll fall back to a clickable preview
    // Note: Google Maps zoom levels: 1=world, 2=continent, 3=country, 4=region, 5=city
    // For Google Earth Web, we use the zoom parameter directly
    const embedUrl = `https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d${Math.floor(Math.pow(2, coords.zoom) * 100)}!2d${coords.lng}!3d${coords.lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v${Date.now()}!5m2!1sen!2sus`;
    
    // Add map selection mode controls
    const mapControlsHtml = window.appState.mapSelectionMode ? `
        <div style="position: absolute; top: 10px; right: 10px; background: rgba(74,158,255,0.9); padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); z-index: 10; pointer-events: auto;">
            <strong>📍 Selection Mode</strong><br>
            <small>Click on map to set filter</small>
        </div>
    ` : '';
    
    const html = `
        <div style="position: relative; width: 100%; height: 100%; border-radius: 8px; overflow: hidden;">
            <iframe 
                id="earth-iframe"
                src="${embedUrl}"
                width="100%"
                height="100%"
                style="border:0; border-radius: 8px; ${window.appState.mapSelectionMode ? 'cursor: crosshair;' : ''}"
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
                title="Earth View - ${escapeHtml(continent)}"
                onerror="this.parentElement.innerHTML='<div style=\\'padding: 40px; text-align: center; color: rgba(255,255,255,0.7);\\'><div style=\\'font-size: 3rem; margin-bottom: 10px;\\'>🌍</div><p>${escapeHtml(continent)}</p><a href=\\'${mapsLink}\\' target=\\'_blank\\' style=\\'color: #4a9eff; text-decoration: none;\\'>Open in Google Maps</a></div>'">
            </iframe>
            ${mapControlsHtml}
            <div style="position: absolute; bottom: 10px; right: 10px; display: flex; gap: 8px; z-index: 10; pointer-events: none; flex-direction: column; align-items: flex-end;">
                ${window.appState.mapFilter ? `
                <button onclick="clearMapFilter()" style="background: rgba(220,53,69,0.9); color: #fff; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; border: none; cursor: pointer; pointer-events: auto; margin-bottom: 8px; backdrop-filter: blur(10px);">
                    ✕ Clear Filter
                </button>
                ` : ''}
                <button onclick="toggleMapSelectionMode()" style="background: rgba(0,0,0,0.85); color: #4a9eff; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.2); cursor: pointer; pointer-events: auto; backdrop-filter: blur(10px); margin-bottom: 8px;">
                    ${window.appState.mapSelectionMode ? '✓' : '📍'} Select Location
                </button>
                <a href="${earthLink}" target="_blank" 
                   style="background: rgba(0,0,0,0.85); color: #4a9eff; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; text-decoration: none; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease; display: inline-block; pointer-events: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3);"
                   onmouseover="this.style.background='rgba(74,158,255,0.4)'; this.style.color='#fff'; this.style.transform='translateY(-2px)';"
                   onmouseout="this.style.background='rgba(0,0,0,0.85)'; this.style.color='#4a9eff'; this.style.transform='translateY(0)';">
                    🌍 Google Earth
                </a>
            </div>
            <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); pointer-events: none; z-index: 10;">
                <strong>${escapeHtml(continent)}</strong>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Note: Google Maps iframe doesn't support click events directly
    // For full map selection, we'd need Google Maps API or a different approach
    // For now, we'll add a workaround using a clickable overlay or external link
}

// Highlight an event on the timeline by ID
function highlightEventOnTimeline(eventId, eventData) {
    if (!timelineContainer || !eventId) return;
    
    const graphDiv = timelineContainer;
    
    // Find the trace and point that matches this event ID
    if (!graphDiv.data) return;
    
    // Clear any existing highlights first
    clearEventHighlight();
    
    // Search through all traces to find the point with matching ID
    for (let traceIndex = 0; traceIndex < graphDiv.data.length; traceIndex++) {
        const trace = graphDiv.data[traceIndex];
        
        if (trace.customdata && Array.isArray(trace.customdata)) {
            for (let pointIndex = 0; pointIndex < trace.customdata.length; pointIndex++) {
                const customdata = trace.customdata[pointIndex];
                const pointId = Array.isArray(customdata) ? customdata[0] : (customdata?.id || null);
                
                if (pointId === eventId || pointId === String(eventId)) {
                    // Found the point! Add a highlight overlay trace
                    const x = trace.x[pointIndex];
                    const y = trace.y[pointIndex];
                    
                    // Get the trace's original color for reference
                    const originalColor = Array.isArray(trace.marker.color) 
                        ? trace.marker.color[pointIndex] 
                        : trace.marker.color;
                    
                    // Add a highlight trace (larger, gold marker on top)
                    const highlightTrace = {
                        x: [x],
                        y: [y],
                        mode: 'markers',
                        type: 'scatter',
                        marker: {
                            size: 20,
                            color: 'rgba(255, 215, 0, 1)', // Gold
                            line: {
                                width: 3,
                                color: 'rgba(255, 255, 255, 1)'
                            },
                            symbol: 'circle',
                            opacity: 1
                        },
                        showlegend: false,
                        hoverinfo: 'skip',
                        name: '_highlight'
                    };
                    
                    // Add the highlight trace
                    Plotly.addTraces(graphDiv, highlightTrace);
                    
                    // Also populate event details (which will update Earth view)
                    if (eventData) {
                        populateEventDetails(eventData);
                    } else if (customdata) {
                        populateEventDetails(customdata);
                    }
                    
                    // Store highlight info for clearing later
                    window.highlightedTraceIndex = graphDiv.data.length - 1; // Last trace is the highlight
                    window.highlightedEventId = eventId;
                    
                    console.log(`Highlighted event: ${eventId} at trace ${traceIndex}, point ${pointIndex}`);
                    return;
                }
            }
        }
    }
    
    console.warn(`Event with ID ${eventId} not found on timeline`);
}

// Clear event highlight
function clearEventHighlight() {
    if (window.highlightedTraceIndex === undefined || !timelineContainer) return;
    
    const graphDiv = timelineContainer;
    const traceIndex = window.highlightedTraceIndex;
    
    // Remove the highlight trace (it's the last one we added)
    if (graphDiv.data && graphDiv.data[traceIndex] && graphDiv.data[traceIndex].name === '_highlight') {
        Plotly.deleteTraces(graphDiv, traceIndex);
    }
    
    // Clear highlight info
    delete window.highlightedTraceIndex;
    delete window.highlightedEventId;
}

// Enable fluid scrolling with mouse wheel/trackpad
function enableFluidScrolling(graphDiv) {
    if (!graphDiv) return;
    
    let scrollTimeout = null;
    
    // Handle wheel events (mouse wheel and trackpad)
    // Use DOM event listener, not Plotly's event system
    graphDiv.addEventListener('wheel', (event) => {
        // Only handle if we have valid layout data
        if (!graphDiv.layout || !graphDiv.layout.xaxis || !graphDiv.layout.xaxis.range) {
            return;
        }
        
        event.preventDefault();
        event.stopPropagation();
        
        // Get current axis ranges
        const currentRange = graphDiv.layout.xaxis.range;
        const currentStart = currentRange[0];
        const currentEnd = currentRange[1];
        const currentSpan = currentEnd - currentStart;
        
        // Determine if zoom (with modifier) or pan (normal scroll)
        const isZoom = event.ctrlKey || event.metaKey || event.shiftKey;
        
        // Get scroll delta (normalize for different browsers/devices)
        let deltaY = event.deltaY;
        if (event.deltaMode === 1) {
            // Line mode
            deltaY *= 40;
        } else if (event.deltaMode === 2) {
            // Page mode
            deltaY *= 400;
        }
        
        // Smooth scrolling factors (adjust for sensitivity)
        const panFactor = 0.0008; // How much to pan per scroll unit
        const zoomFactor = 0.03; // How much to zoom per scroll unit
        
        if (isZoom) {
            // Zoom in/out centered on mouse position
            const rect = graphDiv.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const centerX = Math.max(0, Math.min(1, mouseX / rect.width));
            
            const centerYear = currentStart + (currentSpan * centerX);
            
            // Calculate zoom (negative because scroll down should zoom out)
            const zoomAmount = -deltaY * zoomFactor;
            const zoomRatio = 1 + zoomAmount;
            
            // Calculate new range centered on the zoom point
            const newSpan = currentSpan * zoomRatio;
            const newStart = centerYear - (newSpan * centerX);
            const newEnd = centerYear + (newSpan * (1 - centerX));
            
            // Apply zoom
            Plotly.relayout(graphDiv, {
                'xaxis.range': [newStart, newEnd]
            });
        } else {
            // Pan left/right (vertical scroll pans horizontally through time)
            const panAmount = -deltaY * panFactor * currentSpan; // Negative for natural scrolling
            const newStart = currentStart + panAmount;
            const newEnd = currentEnd + panAmount;
            
            // Apply pan
            Plotly.relayout(graphDiv, {
                'xaxis.range': [newStart, newEnd]
            });
        }
        
        // Update backdrop after scroll (debounced)
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const newRange = graphDiv.layout.xaxis.range;
            if (newRange && newRange[0] !== undefined && newRange[1] !== undefined) {
                const midYear = (newRange[0] + newRange[1]) / 2;
                if (typeof setBackdropForYear === 'function') {
                    setBackdropForYear(midYear);
                }
            }
        }, 150);
    }, { passive: false });
    
    // Also handle touchpad pinch-to-zoom (for trackpads)
    let lastTouchDistance = 0;
    let isPinching = false;
    
    graphDiv.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            isPinching = true;
            const touch1 = e.touches[0];
            const touch2 = e.touches[1];
            lastTouchDistance = Math.hypot(
                touch2.clientX - touch1.clientX,
                touch2.clientY - touch1.clientY
            );
        }
    });
    
    graphDiv.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2 && isPinching) {
            e.preventDefault();
            const touch1 = e.touches[0];
            const touch2 = e.touches[1];
            const currentDistance = Math.hypot(
                touch2.clientX - touch1.clientX,
                touch2.clientY - touch1.clientY
            );
            
            if (lastTouchDistance > 0) {
                const layout = graphDiv.layout;
                if (layout && layout.xaxis && layout.xaxis.range) {
                    const currentRange = layout.xaxis.range;
                    const currentStart = currentRange[0];
                    const currentEnd = currentRange[1];
                    const currentSpan = currentEnd - currentStart;
                    
                    const zoomRatio = currentDistance / lastTouchDistance;
                    const newSpan = currentSpan / zoomRatio;
                    const centerYear = (currentStart + currentEnd) / 2;
                    const newStart = centerYear - newSpan / 2;
                    const newEnd = centerYear + newSpan / 2;
                    
                    Plotly.relayout(graphDiv, {
                        'xaxis.range': [newStart, newEnd]
                    });
                }
            }
            
            lastTouchDistance = currentDistance;
        }
    });
    
    graphDiv.addEventListener('touchend', () => {
        isPinching = false;
        lastTouchDistance = 0;
    });
}

// Import CSV functionality
async function checkImportStatus() {
    try {
        if (!importStatusContainer) return;
        
        importStatusContainer.innerHTML = '<div class="loading">Checking status...</div>';
        
        const response = await fetch('/api/import-status');
        const result = await response.json();
        
        if (result.error) {
            importStatusContainer.innerHTML = `<div class="error">Error: ${result.error}</div>`;
            return;
        }
        
        let statusHtml = `
            <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; margin-bottom: 15px;">
                <strong>Current Status:</strong><br>
                Events in database: <strong>${result.total_events}</strong><br>
                CSV file: ${result.csv_file_exists ? '✓ Found' : '✗ Not found'}
            </div>
        `;
        
        if (result.total_events === 0) {
            statusHtml += '<p style="color: #ffd700;">⚠️ No events in database. Click "Import CSV" to import from timeline_data_4.csv</p>';
        } else {
            statusHtml += `<p style="color: #6cff87;">✓ Database has ${result.total_events} events. You can add more or clear and re-import.</p>`;
        }
        
        importStatusContainer.innerHTML = statusHtml;
        
    } catch (error) {
        console.error('Error checking import status:', error);
        if (importStatusContainer) {
            importStatusContainer.innerHTML = `<div class="error">Error checking status: ${error.message}</div>`;
        }
    }
}

async function importCsv(clearExisting = false) {
    try {
        if (!importResultDiv) return;
        
        importResultDiv.innerHTML = '<div class="loading">Importing CSV data...</div>';
        
        const url = clearExisting ? '/api/import-csv?clear=true' : '/api/import-csv';
        const response = await fetch(url, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Import failed');
        }
        
        let resultHtml = `
            <div style="padding: 15px; background: rgba(40, 167, 69, 0.2); border: 1px solid rgba(40, 167, 69, 0.5); border-radius: 8px; color: #6cff87;">
                <strong>✓ Import Complete!</strong><br>
                Imported: <strong>${result.imported}</strong> events<br>
                Skipped: ${result.skipped} events
        `;
        
        if (result.total_errors > 0) {
            resultHtml += `<br>Errors: ${result.total_errors}`;
            if (result.errors && result.errors.length > 0) {
                resultHtml += '<ul style="margin-top: 10px; font-size: 0.9em;">';
                result.errors.forEach(err => {
                    resultHtml += `<li>${escapeHtml(err)}</li>`;
                });
                resultHtml += '</ul>';
            }
        }
        
        resultHtml += '</div>';
        
        importResultDiv.innerHTML = resultHtml;
        
        // Refresh status and events list
        await checkImportStatus();
        
        // Reload timeline
        const currentStart = parseInt(startYearInput.value);
        const currentEnd = parseInt(endYearInput.value);
        await loadTimeline(currentStart, currentEnd);
        
        // If manage events modal is open, refresh it
        if (manageEventsModal && !manageEventsModal.classList.contains('hidden')) {
            await loadEventsList();
        }
        
    } catch (error) {
        console.error('Error importing CSV:', error);
        if (importResultDiv) {
            importResultDiv.innerHTML = `<div class="error">Error importing CSV: ${error.message}</div>`;
        }
    }
}

