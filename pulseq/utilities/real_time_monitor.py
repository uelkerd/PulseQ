import json
import os
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import requests
from flask import Flask, jsonify, render_template_string
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class BrowserMetrics:
    # Memory metrics
    js_heap_size: float
    js_heap_limit: float
    total_js_heap_size: float
    used_js_heap_size: float

    # DOM metrics
    dom_node_count: int
    dom_element_count: int
    dom_depth: int
    dom_listeners: int

    # Performance metrics
    fps: float
    paint_time: float
    first_contentful_paint: float
    largest_contentful_paint: float
    first_input_delay: float
    cumulative_layout_shift: float
    time_to_interactive: float

    # Resource metrics
    resource_count: int
    resource_load_time: float
    cached_resources: int

    # Script metrics
    script_execution_time: float
    parsing_time: float
    compilation_time: float

    # Layout metrics
    layout_duration: float
    recalc_style_duration: float
    composite_duration: float


@dataclass
class NetworkLatency:
    latency_ms: float
    packet_loss: float
    bandwidth_mbps: float
    dns_lookup_ms: float
    tcp_connection_ms: float
    tls_handshake_ms: float
    ttfb_ms: float


@dataclass
class AlertThresholds:
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    latency_threshold: float = 1000.0
    disk_io_threshold: float = 100_000_000
    js_heap_threshold: float = 80.0
    dom_depth_threshold: float = 32
    fps_threshold: float = 30.0
    fid_threshold: float = 100.0
    cls_threshold: float = 0.1
    resource_load_threshold: float = 5000.0


@dataclass
class AlertChannel:
    type: str  # 'slack', 'email', 'webhook', 'pagerduty', 'teams', 'telegram'
    config: Dict[str, Any]
    severity_level: str = "info"  # 'info', 'warning', 'error', 'critical'
    enabled: bool = True


@dataclass
class AlertConfig:
    thresholds: AlertThresholds = AlertThresholds()
    channels: List[AlertChannel] = None
    alert_cooldown: int = 300  # seconds
    aggregation_window: int = 60  # seconds
    alert_history_size: int = 1000


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    process_count: int
    thread_count: int
    timestamp: str
    browser_metrics: Optional[BrowserMetrics] = None
    network_latency: Optional[NetworkLatency] = None
    alerts: List[str] = None


class RealTimeMonitor:
    def __init__(self, update_interval: float = 1.0, alert_config: AlertConfig = None):
        self.update_interval = update_interval
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 3600
        self.running = False
        self.alert_config = alert_config or AlertConfig()
        self.driver: Optional[WebDriver] = None
        self._setup_flask_app()

    def set_webdriver(self, driver: WebDriver):
        """Set WebDriver instance for browser metrics collection."""
        self.driver = driver

    def _collect_browser_metrics(self) -> Optional[BrowserMetrics]:
        """Collect detailed browser-specific performance metrics."""
        if not self.driver:
            return None

        try:
            # Memory metrics
            memory_metrics = self.driver.execute_script("""
                const memory = window.performance.memory || {};
                return {
                    jsHeapSize: memory.usedJSHeapSize / (1024 * 1024),
                    jsHeapLimit: memory.jsHeapSizeLimit / (1024 * 1024),
                    totalJsHeapSize: memory.totalJSHeapSize / (1024 * 1024),
                    usedJsHeapSize: memory.usedJSHeapSize / (1024 * 1024)
                };
            """)

            # DOM metrics
            dom_metrics = self.driver.execute_script("""
                function getMaxDOMDepth(node, depth = 0) {
                    if (!node.children.length) return depth;
                    return Math.max(...Array.from(node.children).map(child => 
                        getMaxDOMDepth(child, depth + 1)
                    ));
                }
                
                const listeners = window.getEventListeners ? 
                    Object.values(window.getEventListeners(document)).flat().length : 
                    document.querySelectorAll('[onclick], [onchange], [onsubmit]').length;
                
                return {
                    nodeCount: document.getElementsByTagName('*').length,
                    elementCount: document.getElementsByTagName('*').length,
                    domDepth: getMaxDOMDepth(document.documentElement),
                    eventListeners: listeners
                };
            """)

            # Performance metrics
            perf_metrics = self.driver.execute_script("""
                const perf = window.performance;
                const paint = perf.getEntriesByType('paint');
                const nav = perf.getEntriesByType('navigation')[0];
                const fid = perf.getEntriesByType('first-input')[0];
                const cls = performance.getEntriesByType('layout-shift')
                    .reduce((sum, entry) => sum + entry.value, 0);
                
                return {
                    fps: perf.now() / 1000,
                    paintTime: paint[0] ? paint[0].duration : 0,
                    fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                    lcp: performance.getEntriesByName('largest-contentful-paint')[0]?.startTime || 0,
                    fid: fid ? fid.processingStart - fid.startTime : 0,
                    cls: cls,
                    tti: nav ? nav.domInteractive : 0
                };
            """)

            # Resource metrics
            resource_metrics = self.driver.execute_script("""
                const resources = performance.getEntriesByType('resource');
                return {
                    resourceCount: resources.length,
                    loadTime: resources.reduce((sum, r) => sum + r.duration, 0),
                    cachedResources: resources.filter(r => r.transferSize === 0).length
                };
            """)

            # Script and layout metrics
            timing_metrics = self.driver.execute_script("""
                const timing = performance.timing;
                const entries = performance.getEntriesByType('measure');
                
                return {
                    scriptTime: timing.domComplete - timing.domInteractive,
                    parsingTime: timing.domInteractive - timing.responseEnd,
                    compilationTime: entries.find(e => e.name === 'script-compile')?.duration || 0,
                    layoutDuration: entries.find(e => e.name === 'layout')?.duration || 0,
                    styleDuration: entries.find(e => e.name === 'recalc-style')?.duration || 0,
                    compositeDuration: entries.find(e => e.name === 'composite')?.duration || 0
                };
            """)

            return BrowserMetrics(
                # Memory metrics
                js_heap_size=memory_metrics["jsHeapSize"],
                js_heap_limit=memory_metrics["jsHeapLimit"],
                total_js_heap_size=memory_metrics["totalJsHeapSize"],
                used_js_heap_size=memory_metrics["usedJsHeapSize"],
                # DOM metrics
                dom_node_count=dom_metrics["nodeCount"],
                dom_element_count=dom_metrics["elementCount"],
                dom_depth=dom_metrics["domDepth"],
                dom_listeners=dom_metrics["eventListeners"],
                # Performance metrics
                fps=perf_metrics["fps"],
                paint_time=perf_metrics["paintTime"],
                first_contentful_paint=perf_metrics["fcp"],
                largest_contentful_paint=perf_metrics["lcp"],
                first_input_delay=perf_metrics["fid"],
                cumulative_layout_shift=perf_metrics["cls"],
                time_to_interactive=perf_metrics["tti"],
                # Resource metrics
                resource_count=resource_metrics["resourceCount"],
                resource_load_time=resource_metrics["loadTime"],
                cached_resources=resource_metrics["cachedResources"],
                # Script metrics
                script_execution_time=timing_metrics["scriptTime"],
                parsing_time=timing_metrics["parsingTime"],
                compilation_time=timing_metrics["compilationTime"],
                # Layout metrics
                layout_duration=timing_metrics["layoutDuration"],
                recalc_style_duration=timing_metrics["styleDuration"],
                composite_duration=timing_metrics["compositeDuration"],
            )
        except Exception as e:
            print(f"Error collecting browser metrics: {e}")
            return None

    def _collect_network_latency(self) -> NetworkLatency:
        """Collect detailed network latency metrics."""
        # Measure basic latency with ping
        ping_output = subprocess.run(
            ["ping", "-c", "1", "google.com"], capture_output=True, text=True
        )
        latency = float(ping_output.stdout.split("time=")[-1].split()[0])

        # Measure packet loss
        ping_stats = subprocess.run(
            ["ping", "-c", "10", "google.com"], capture_output=True, text=True
        )
        packet_loss = float(ping_stats.stdout.split("%")[0].split()[-1])

        # Measure bandwidth using speedtest-cli (if available)
        try:
            import speedtest

            st = speedtest.Speedtest()
            bandwidth = st.download() / 1_000_000  # Convert to Mbps
        except:
            bandwidth = 0

        # Measure DNS and TCP metrics
        start_time = time.time()
        session = requests.Session()

        # DNS lookup
        dns_start = time.time()
        session.get("https://google.com")
        dns_time = (time.time() - dns_start) * 1000

        # TCP connection
        tcp_start = time.time()
        session.get("https://google.com")
        tcp_time = (time.time() - tcp_start) * 1000

        # TLS handshake
        tls_start = time.time()
        session.get("https://google.com")
        tls_time = (time.time() - tls_start) * 1000

        # TTFB
        ttfb_start = time.time()
        response = session.get("https://google.com")
        ttfb = response.elapsed.total_seconds() * 1000

        return NetworkLatency(
            latency_ms=latency,
            packet_loss=packet_loss,
            bandwidth_mbps=bandwidth,
            dns_lookup_ms=dns_time,
            tcp_connection_ms=tcp_time,
            tls_handshake_ms=tls_time,
            ttfb_ms=ttfb,
        )

    def _check_alerts(self, metrics: SystemMetrics) -> List[str]:
        """Check for metric threshold violations."""
        alerts = []

        if metrics.cpu_percent > self.alert_config.thresholds.cpu_threshold:
            alerts.append(f"CPU usage ({metrics.cpu_percent}%) exceeded threshold")

        if metrics.memory_percent > self.alert_config.thresholds.memory_threshold:
            alerts.append(
                f"Memory usage ({metrics.memory_percent}%) exceeded threshold"
            )

        if (
            metrics.network_latency
            and metrics.network_latency.latency_ms
            > self.alert_config.thresholds.latency_threshold
        ):
            alerts.append(
                f"Network latency ({metrics.network_latency.latency_ms}ms) exceeded threshold"
            )

        if (
            metrics.disk_io["write_bytes"]
            > self.alert_config.thresholds.disk_io_threshold
        ):
            alerts.append(
                f"Disk write I/O ({metrics.disk_io['write_bytes']/1_000_000:.1f}MB/s) exceeded threshold"
            )

        return alerts

    def _send_alerts(self, alerts: List[str]):
        """Send alerts through configured channels with enhanced functionality."""
        if not alerts or not self.alert_config.channels:
            return

        timestamp = datetime.now().isoformat()

        for channel in self.alert_config.channels:
            if not channel.enabled:
                continue

            try:
                if channel.type == "slack":
                    self._send_slack_alert(alerts, channel, timestamp)
                elif channel.type == "email":
                    self._send_email_alert(alerts, channel, timestamp)
                elif channel.type == "pagerduty":
                    self._send_pagerduty_alert(alerts, channel, timestamp)
                elif channel.type == "teams":
                    self._send_teams_alert(alerts, channel, timestamp)
                elif channel.type == "telegram":
                    self._send_telegram_alert(alerts, channel, timestamp)
                elif channel.type == "webhook":
                    self._send_webhook_alert(alerts, channel, timestamp)
            except Exception as e:
                print(f"Error sending alert to {channel.type}: {e}")

    def _send_slack_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send enhanced Slack alerts with metrics and visualizations."""
        webhook_url = channel.config.get("webhook_url")
        if not webhook_url:
            return

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 Performance Alert"},
            }
        ]

        for alert in alerts:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Alert:* {alert}\n*Time:* {timestamp}\n*Severity:* {channel.severity_level}",
                    },
                }
            )

        requests.post(webhook_url, json={"blocks": blocks})

    def _send_email_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send alert via email."""
        # Implementation depends on your email configuration
        pass

    def _send_webhook_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send alert to webhook."""
        # Implementation depends on your webhook configuration
        pass

    def _send_pagerduty_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send alerts to PagerDuty."""
        api_key = channel.config.get("api_key")
        service_id = channel.config.get("service_id")

        if not api_key or not service_id:
            return

        headers = {
            "Authorization": f"Token token={api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "incident": {
                "type": "incident",
                "title": "Performance Alert",
                "service": {"id": service_id},
                "urgency": (
                    "high" if channel.severity_level in ["error", "critical"] else "low"
                ),
                "body": {"type": "incident_body", "details": "\n".join(alerts)},
            }
        }

        requests.post(
            "https://api.pagerduty.com/incidents", headers=headers, json=payload
        )

    def _send_teams_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send alerts to Microsoft Teams."""
        webhook_url = channel.config.get("webhook_url")
        if not webhook_url:
            return

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Performance Alert",
            "sections": [
                {
                    "activityTitle": "🚨 Performance Alert",
                    "activitySubtitle": timestamp,
                    "facts": [{"name": "Severity", "value": channel.severity_level}],
                    "text": "\n\n".join(alerts),
                }
            ],
        }

        requests.post(webhook_url, json=payload)

    def _send_telegram_alert(
        self, alerts: List[str], channel: AlertChannel, timestamp: str
    ):
        """Send alerts to Telegram."""
        bot_token = channel.config.get("bot_token")
        chat_id = channel.config.get("chat_id")

        if not bot_token or not chat_id:
            return

        message = f"🚨 *Performance Alert*\n\n"
        message += f"*Time:* {timestamp}\n"
        message += f"*Severity:* {channel.severity_level}\n\n"
        message += "\n".join(f"• {alert}" for alert in alerts)

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
        )

    def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics with enhanced monitoring."""
        process = psutil.Process()

        # Get disk I/O
        disk_io = psutil.disk_io_counters()
        disk_metrics = {
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0,
        }

        # Get network I/O
        net_io = psutil.net_io_counters()
        net_metrics = {
            "bytes_sent": net_io.bytes_sent if net_io else 0,
            "bytes_recv": net_io.bytes_recv if net_io else 0,
        }

        # Collect browser metrics if available
        browser_metrics = self._collect_browser_metrics()

        # Collect network latency metrics
        network_latency = self._collect_network_latency()

        metrics = SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_io=disk_metrics,
            network_io=net_metrics,
            process_count=len(psutil.pids()),
            thread_count=process.num_threads(),
            timestamp=datetime.now().isoformat(),
            browser_metrics=browser_metrics,
            network_latency=network_latency,
            alerts=[],
        )

        # Check for alerts
        alerts = self._check_alerts(metrics)
        if alerts:
            metrics.alerts = alerts
            self._send_alerts(alerts)

        return metrics

    def _setup_flask_app(self):
        self.app = Flask(__name__)

        @self.app.route("/")
        def dashboard():
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>PulseQ Performance Dashboard</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    <script src="https://d3js.org/d3.v7.min.js"></script>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }
                        .chart { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                        .metrics-panel { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                        .alert { background: #ff6b6b; color: white; padding: 10px; margin: 5px 0; border-radius: 3px; }
                        .waterfall { height: 300px; }
                        .flame-graph { height: 300px; }
                        .metric-group { margin-bottom: 15px; }
                        .metric-title { font-weight: bold; margin-bottom: 5px; }
                        .metric-value { font-family: monospace; }
                    </style>
                </head>
                <body>
                    <h1>PulseQ Real-Time Performance Dashboard</h1>
                    
                    <!-- Alerts Panel -->
                    <div id="alertsPanel" class="metrics-panel">
                        <h2>Active Alerts</h2>
                        <div id="alerts"></div>
                    </div>

                    <!-- System Metrics -->
                    <div class="grid">
                        <div class="chart">
                            <div id="cpuChart"></div>
                        </div>
                        <div class="chart">
                            <div id="memoryChart"></div>
                        </div>
                        <div class="chart">
                            <div id="diskChart"></div>
                        </div>
                        <div class="chart">
                            <div id="networkChart"></div>
                        </div>
                    </div>

                    <!-- Browser Metrics -->
                    <div class="grid">
                        <div class="chart">
                            <div id="browserMemoryChart"></div>
                        </div>
                        <div class="chart">
                            <div id="paintTimingChart"></div>
                        </div>
                        <div class="chart">
                            <div id="fpsChart"></div>
                        </div>
                        <div class="chart">
                            <div id="domMetricsChart"></div>
                        </div>
                    </div>

                    <!-- Network Latency -->
                    <div class="grid">
                        <div class="chart">
                            <div id="latencyWaterfall"></div>
                        </div>
                        <div class="chart">
                            <div id="networkLatencyChart"></div>
                        </div>
                    </div>

                    <!-- Detailed Metrics Panel -->
                    <div class="metrics-panel">
                        <h2>Detailed Metrics</h2>
                        <div id="detailedMetrics"></div>
                    </div>

                    <script>
                        function updateCharts() {
                            fetch('/metrics')
                                .then(response => response.json())
                                .then(data => {
                                    const timestamps = data.map(d => d.timestamp);
                                    
                                    // Update system metrics
                                    updateSystemMetrics(data, timestamps);
                                    
                                    // Update browser metrics
                                    updateBrowserMetrics(data, timestamps);
                                    
                                    // Update network metrics
                                    updateNetworkMetrics(data, timestamps);
                                    
                                    // Update alerts
                                    updateAlerts(data);
                                    
                                    // Update detailed metrics panel
                                    updateDetailedMetrics(data[data.length - 1]);
                                });
                        }

                        function updateSystemMetrics(data, timestamps) {
                            Plotly.newPlot('cpuChart', [{
                                x: timestamps,
                                y: data.map(d => d.cpu_percent),
                                name: 'CPU Usage',
                                fill: 'tozeroy'
                            }], {
                                title: 'CPU Usage (%)',
                                showlegend: false
                            });
                            
                            Plotly.newPlot('memoryChart', [{
                                x: timestamps,
                                y: data.map(d => d.memory_percent),
                                name: 'Memory Usage',
                                fill: 'tozeroy'
                            }], {
                                title: 'Memory Usage (%)',
                                showlegend: false
                            });
                        }

                        function updateBrowserMetrics(data, timestamps) {
                            const browserData = data.filter(d => d.browser_metrics);
                            
                            if (browserData.length > 0) {
                                Plotly.newPlot('browserMemoryChart', [{
                                    x: timestamps,
                                    y: browserData.map(d => d.browser_metrics.js_heap_size),
                                    name: 'JS Heap Size'
                                }], {
                                    title: 'JavaScript Heap Size (MB)'
                                });

                                Plotly.newPlot('paintTimingChart', [{
                                    x: timestamps,
                                    y: browserData.map(d => d.browser_metrics.paint_time),
                                    name: 'Paint Time'
                                }], {
                                    title: 'Paint Timing (ms)'
                                });
                            }
                        }

                        function updateNetworkMetrics(data, timestamps) {
                            const networkData = data.filter(d => d.network_latency);
                            
                            if (networkData.length > 0) {
                                const latencyData = {
                                    x: ['DNS', 'TCP', 'TLS', 'TTFB'],
                                    y: [
                                        networkData[networkData.length - 1].network_latency.dns_lookup_ms,
                                        networkData[networkData.length - 1].network_latency.tcp_connection_ms,
                                        networkData[networkData.length - 1].network_latency.tls_handshake_ms,
                                        networkData[networkData.length - 1].network_latency.ttfb_ms
                                    ],
                                    type: 'waterfall'
                                };

                                Plotly.newPlot('latencyWaterfall', [latencyData], {
                                    title: 'Network Latency Breakdown'
                                });
                            }
                        }

                        function updateAlerts(data) {
                            const alertsDiv = document.getElementById('alerts');
                            const latestMetrics = data[data.length - 1];
                            
                            if (latestMetrics.alerts && latestMetrics.alerts.length > 0) {
                                alertsDiv.innerHTML = latestMetrics.alerts
                                    .map(alert => `<div class="alert">${alert}</div>`)
                                    .join('');
                            } else {
                                alertsDiv.innerHTML = '<p>No active alerts</p>';
                            }
                        }

                        function updateDetailedMetrics(metrics) {
                            const detailedMetricsDiv = document.getElementById('detailedMetrics');
                            
                            const html = `
                                <div class="metric-group">
                                    <div class="metric-title">System</div>
                                    <div class="metric-value">CPU: ${metrics.cpu_percent}%</div>
                                    <div class="metric-value">Memory: ${metrics.memory_percent}%</div>
                                    <div class="metric-value">Processes: ${metrics.process_count}</div>
                                    <div class="metric-value">Threads: ${metrics.thread_count}</div>
                                </div>
                                ${metrics.browser_metrics ? `
                                    <div class="metric-group">
                                        <div class="metric-title">Browser</div>
                                        <div class="metric-value">JS Heap: ${metrics.browser_metrics.js_heap_size.toFixed(2)} MB</div>
                                        <div class="metric-value">DOM Nodes: ${metrics.browser_metrics.dom_node_count}</div>
                                        <div class="metric-value">FPS: ${metrics.browser_metrics.fps.toFixed(2)}</div>
                                        <div class="metric-value">FCP: ${metrics.browser_metrics.first_contentful_paint.toFixed(2)}ms</div>
                                    </div>
                                ` : ''}
                                ${metrics.network_latency ? `
                                    <div class="metric-group">
                                        <div class="metric-title">Network</div>
                                        <div class="metric-value">Latency: ${metrics.network_latency.latency_ms.toFixed(2)}ms</div>
                                        <div class="metric-value">Packet Loss: ${metrics.network_latency.packet_loss.toFixed(2)}%</div>
                                        <div class="metric-value">Bandwidth: ${metrics.network_latency.bandwidth_mbps.toFixed(2)} Mbps</div>
                                    </div>
                                ` : ''}
                            `;
                            
                            detailedMetricsDiv.innerHTML = html;
                        }

                        // Update every second
                        setInterval(updateCharts, 1000);
                        updateCharts();
                    </script>
                </body>
                </html>
            """)

        @self.app.route("/metrics")
        def get_metrics():
            return jsonify([asdict(m) for m in self.metrics_history])

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)

            # Keep only recent history
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history :]

            time.sleep(self.update_interval)

    def start(self, port: int = 5000):
        """Start the monitoring dashboard."""
        self.running = True

        # Start metrics collection in background
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        # Start Flask app
        self.app.run(port=port, debug=False)

    def stop(self):
        """Stop the monitoring dashboard."""
        self.running = False
        if hasattr(self, "monitor_thread"):
            self.monitor_thread.join(timeout=1.0)
