<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Traffic Capture Dashboard</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
</head>

<body class="dark-theme">
    <div class="container">
        <header>
            <div class="logo">
                <span class="pulse"></span>
                <h1>SEO <span>Capture</span></h1>
            </div>
            <div class="status">
                <span id="last-update">Updating...</span>
            </div>
        </header>

        <section class="hero-stats">
            <div class="stat-card glass" id="total-trends">
                <h3>Top 24h Trend</h3>
                <p class="value">--</p>
                <p class="label">Loading...</p>
            </div>
            <div class="stat-card glass breakout" id="priority-alert">
                <h3>High Priority</h3>
                <p class="value">0</p>
                <p class="label">Alerts Found</p>
            </div>
        </section>

        <main>
            <section class="card-grid">
                <div class="card glass recent-sightings">
                    <div class="card-header">
                        <h2>Real-time Sightings</h2>
                        <button id="refresh-btn">Refresh</button>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Keyword</th>
                                    <th>Domain</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody id="sightings-table">
                                <!-- Data injected here -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card glass top-keywords">
                    <div class="card-header">
                        <h2>Power Gain (24h)</h2>
                    </div>
                    <div class="chart-list" id="top-keywords-list">
                        <!-- Data injected here -->
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <p>&copy; 2026 Custom SEO News Tool. Powered by GitHub Actions & Hostinger.</p>
        </footer>
    </div>
    <script src="app.js"></script>
</body>

</html>