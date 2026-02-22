<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Database credentials - Hostinger
$db_host = 'srv2124.hstgr.io';
$db_user = 'u571414736_njkkkkk';
$db_pass = '+/dAT3b3r&HXB*-';
$db_name = 'u571414736_njkkkkk';

try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8", $db_user, $db_pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $action = $_GET['action'] ?? 'recent';

    if ($action === 'recent') {
        // Get the last 100 sightings
        $stmt = $pdo->query("SELECT * FROM keyword_sightings ORDER BY timestamp DESC LIMIT 100");
        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode(['status' => 'success', 'data' => $results]);
    } elseif ($action === 'stats') {
        // Get top keywords in the last 24 hours
        $stmt = $pdo->query("
            SELECT keyword, COUNT(*) as sightings, COUNT(DISTINCT source_domain) as unique_sources 
            FROM keyword_sightings 
            WHERE timestamp >= NOW() - INTERVAL 24 HOUR 
            GROUP BY keyword 
            ORDER BY sightings DESC 
            LIMIT 10
        ");
        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode(['status' => 'success', 'data' => $results]);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Invalid action']);
    }
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'Connection failed: ' . $e->getMessage()]);
}
?>
