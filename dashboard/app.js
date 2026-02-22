document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    
    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchData();
    });

    // Auto-refresh every 5 minutes
    setInterval(fetchData, 300000);
});

async function fetchData() {
    try {
        const [recentResponse, statsResponse] = await Promise.all([
            fetch('api.php?action=recent'),
            fetch('api.php?action=stats')
        ]);

        const recentData = await recentResponse.json();
        const statsData = await statsResponse.json();

        if (recentData.status === 'success') {
            updateRecentSightings(recentData.data);
            updateAlerts(recentData.data);
        }

        if (statsData.status === 'success') {
            updateStats(statsData.data);
        }

        document.getElementById('last-update').textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateRecentSightings(sightings) {
    const tableBody = document.getElementById('sightings-table');
    tableBody.innerHTML = '';

    sightings.forEach(item => {
        const row = document.createElement('tr');
        const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        row.innerHTML = `
            <td><span class="keyword-badge">${item.keyword}</span></td>
            <td>${item.source_domain}</td>
            <td style="color: #8b949e">${time}</td>
        `;
        tableBody.appendChild(row);
    });
}

function updateStats(stats) {
    const list = document.getElementById('top-keywords-list');
    list.innerHTML = '';

    if (stats.length > 0) {
        // Hero Stat update
        const topTrend = stats[0];
        document.querySelector('#total-trends .value').textContent = topTrend.keyword;
        document.querySelector('#total-trends .label').textContent = `${topTrend.sightings} sightings from ${topTrend.unique_sources} sources`;

        const maxSightings = Math.max(...stats.map(s => parseInt(s.sightings)));

        stats.forEach(item => {
            const percentage = (parseInt(item.sightings) / maxSightings) * 100;
            const itemEl = document.createElement('div');
            itemEl.className = 'chart-item';
            itemEl.innerHTML = `
                <div class="chart-label">
                    <span>${item.keyword}</span>
                    <span>${item.sightings}</span>
                </div>
                <div class="chart-bar-bg">
                    <div class="chart-bar-fill" style="width: 0%"></div>
                </div>
            `;
            list.appendChild(itemEl);
            
            // Trigger animation
            setTimeout(() => {
                itemEl.querySelector('.chart-bar-fill').style.width = `${percentage}%`;
            }, 100);
        });
    }
}

function updateAlerts(sightings) {
    // Basic logic to find if any keyword appears > 3 times in the recently fetched batch
    const counts = {};
    sightings.forEach(s => {
        counts[s.keyword] = (counts[s.keyword] || 0) + 1;
    });

    let alertsCount = 0;
    for (const kw in counts) {
        if (counts[kw] >= 5) {
            alertsCount++;
        }
    }

    const alertEl = document.getElementById('priority-alert');
    alertEl.querySelector('.value').textContent = alertsCount;
    
    if (alertsCount > 0) {
        alertEl.style.borderColor = 'var(--breakout)';
        alertEl.style.boxShadow = '0 0 15px var(--breakout-glow)';
    } else {
        alertEl.style.borderColor = 'var(--border)';
        alertEl.style.boxShadow = 'none';
    }
}
