const API_URL = 'http://localhost:8800';

const state = {
    events: { page: 0, limit: 10, total: 0 },
    bets: { page: 0, limit: 10, total: 0 }
};

async function fetchEvents() {
    try {
        const offset = state.events.page * state.events.limit;
        const response = await fetch(`${API_URL}/events/?offset=${offset}&limit=${state.events.limit}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        state.events.total = data.total;
        displayEvents(data.events || []);
        updatePaginationInfo('events');
    } catch (error) {
        console.error('Error fetching events:', error);
        document.getElementById('events-list').innerHTML = `
            <div class="alert alert-danger" role="alert">
                Failed to fetch events: ${error.message}
            </div>
        `;
    }
}

function displayEvents(events) {

    const eventsContainer = document.getElementById('events-list');
    if (!eventsContainer) {
        console.error('Events container not found');
        return;
    }

    eventsContainer.innerHTML = '';

    const eventsArray = Array.from(events || []);
    
    if (eventsArray.length === 0) {
        eventsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                No events available at this time.
            </div>
        `;
        return;
    }

    const fragment = document.createDocumentFragment();
    
    for (const event of eventsArray) {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-4';
        card.innerHTML = `
            <div class="card event-card">
                <div class="card-body">
                    <h5 class="card-title">Event #${event.event_id || 'Unknown'}</h5>
                    <p class="card-text">
                        <strong>Coefficient:</strong> ${event.coefficient || 'N/A'}<br>
                        <strong>Deadline:</strong> ${event.deadline ? new Date(event.deadline * 1000).toLocaleString() : 'N/A'}<br>
                        <strong>State:</strong> ${event.state || 'Unknown'}
                    </p>
                    ${event.state === 'NEW' ? `
                        <button class="btn btn-primary" onclick="placeBet(${event.event_id})">Place Bet</button>
                    ` : ''}
                </div>
            </div>
        `;
        fragment.appendChild(card);
    }
    
    // Add all cards to container at once
    eventsContainer.appendChild(fragment);
}

async function fetchBets() {
    try {
        const offset = state.bets.page * state.bets.limit;
        const response = await fetch(`${API_URL}/bets/?offset=${offset}&limit=${state.bets.limit}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        state.bets.total = data.total;
        displayBets(data.bets || []);  
        updatePaginationInfo('bets');
    } catch (error) {
        console.error('Error fetching bets:', error);
        document.getElementById('bets-list').innerHTML = `
            <div class="alert alert-danger" role="alert">
                Failed to fetch bets: ${error.message}
            </div>
        `;
    }
}

function updatePaginationInfo(type) {
    const { page, limit, total } = state[type];
    const totalPages = Math.ceil(total / limit);
    const currentPage = page + 1;
    
    // Update page info
    const pageInfo = document.getElementById(`${type}-page-info`);
    if (pageInfo) {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }
    
    // Update total info
    const totalInfo = document.getElementById(`${type}-total-info`);
    if (totalInfo) {
        totalInfo.textContent = `Total ${type}: ${total}`;
    }
    
    // Update button states
    const prevButton = document.querySelector(`#${type}-container .pagination .page-item:first-child button`);
    const nextButton = document.querySelector(`#${type}-container .pagination .page-item:last-child button`);
    
    if (prevButton) {
        prevButton.disabled = page <= 0;
    }
    if (nextButton) {
        nextButton.disabled = currentPage >= totalPages;
    }
}

function changePage(type, direction) {
    const { page, limit, total } = state[type];
    const totalPages = Math.ceil(total / limit);
    const newPage = direction === 'prev' ? page - 1 : page + 1;
    
    // Validate the new page number
    if (newPage < 0 || newPage >= totalPages) {
        return;
    }
    
    // Update the page number
    state[type].page = newPage;
    
    // Fetch new data
    if (type === 'events') {
        fetchEvents();
    } else {
        fetchBets();
    }
}

function updateItemsPerPage(type) {
    const newLimit = parseInt(document.getElementById(`${type}-per-page`).value);
    state[type].limit = newLimit;
    state[type].page = 0; // Reset to first page
    
    if (type === 'events') {
        fetchEvents();
    } else {
        fetchBets();
    }
}

async function createBet(eventId, amount) {
    try {
        const response = await fetch(`${API_URL}/bet/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_id: eventId,
                amount: parseFloat(amount)
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const bet = await response.json();
        alert('Bet placed successfully!');
        return bet;
    } catch (error) {
        console.error('Error creating bet:', error);
        alert('Failed to place bet: ' + error.message);
    }
}

function displayBets(bets) {
    const betsContainer = document.getElementById('bets-list');
    betsContainer.innerHTML = '';

    bets.forEach(bet => {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-4';
        card.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Bet on Event #${bet.event_id}</h5>
                    <p class="card-text">
                        <strong>Amount:</strong> ${bet.amount}<br>
                        <strong>State:</strong> ${bet.state}<br>
                        <strong>Coefficient:</strong> ${bet.coefficient}
                    </p>
                </div>
            </div>
        `;
        betsContainer.appendChild(card);
    });
}

async function placeBet(eventId) {
    const amountInput = document.getElementById(`amount-${eventId}`);
    const amount = amountInput.value;

    if (!amount || isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    await createBet(eventId, amount);
    fetchEvents();
}

function showBets() {
    const eventsContainer = document.getElementById('events-container');
    const betsContainer = document.getElementById('bets-container');
    const toggleButton = document.getElementById('toggle-view-button');

    if (betsContainer.style.display === 'none') {
        eventsContainer.style.display = 'none';
        betsContainer.style.display = 'block';
        toggleButton.textContent = 'Show Available Events';
        fetchBets();
    } else {
        eventsContainer.style.display = 'block';
        betsContainer.style.display = 'none';
        toggleButton.textContent = 'Show My Bets';
        fetchEvents();
    }
}

// Initial load
fetchEvents();
// Refresh events every 5 seconds
setInterval(fetchEvents, 5000);
