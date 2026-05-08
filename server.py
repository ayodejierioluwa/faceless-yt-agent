import os
import sys
import subprocess
import threading
import time
from flask import Flask, render_template_string, jsonify, request, send_from_directory

app = Flask(__name__)

# Global state to track background generation
state = {
    "running": False,
    "logs": [],
    "progress": 0,
    "start_time": 0
}

# Real-time log capture thread
def run_generation_thread():
    global state
    state["running"] = True
    state["logs"] = []
    state["progress"] = 0
    state["start_time"] = time.time()
    
    # We run python with the -u flag for unbuffered output to get logs instantly
    python_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python3.12")
    if not os.path.exists(python_bin):
        # Fallback to standard python within the venv
        python_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    if not os.path.exists(python_bin):
        python_bin = "python3" # global fallback
        
    cmd = [python_bin, "-u", "main.py"]
    
    state["logs"].append("🤖 Starting Faceless Video Agent Workflow Subprocess...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            if clean_line:
                # Add timestamp to logs
                timestamp = time.strftime("[%H:%M:%S]")
                state["logs"].append(f"{timestamp} {clean_line}")
                
                # Update progress based on keywords
                if "[Step 0]" in clean_line:
                    state["progress"] = 10
                elif "[Step 1]" in clean_line:
                    state["progress"] = 25
                elif "[Step 2]" in clean_line:
                    state["progress"] = 40
                elif "[Step 3]" in clean_line:
                    state["progress"] = 60
                elif "[Step 4]" in clean_line:
                    state["progress"] = 80
                elif "[Step 5]" in clean_line:
                    state["progress"] = 95
                    
        process.stdout.close()
        return_code = process.wait()
        
        if return_code == 0:
            state["progress"] = 100
            state["logs"].append("🎉 WORKFLOW COMPLETED SUCCESSFULLY! Video is ready.")
        else:
            state["logs"].append(f"❌ Subprocess failed with exit code: {return_code}")
            
    except Exception as e:
        state["logs"].append(f"❌ Error during execution: {str(e)}")
    finally:
        state["running"] = False

@app.route("/")
def index():
    # Read environment variables to display in the dashboard
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    env_vars = {}
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r") as f:
            for line in f:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#") and "=" in clean_line:
                    key, val = clean_line.split("=", 1)
                    env_vars[key.strip()] = val.strip()
                    
    # Render premium HTML/CSS dashboard directly
    return render_template_string(HTML_TEMPLATE, env_vars=env_vars, state=state)

@app.route("/api/start", methods=["POST"])
def start_generation():
    global state
    if state["running"]:
        return jsonify({"success": False, "message": "Generation already in progress."}), 400
        
    thread = threading.Thread(target=run_generation_thread)
    thread.daemon = True
    thread.start()
    return jsonify({"success": True, "message": "Generation started in background."})

@app.route("/api/status")
def get_status():
    elapsed = 0
    if state["running"]:
        elapsed = round(time.time() - state["start_time"])
    return jsonify({
        "running": state["running"],
        "progress": state["progress"],
        "elapsed": elapsed,
        "logs": state["logs"]
    })

@app.route("/api/save-config", methods=["POST"])
def save_config():
    data = request.json
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    if not os.path.exists(dotenv_path):
        return jsonify({"success": False, "message": ".env file not found."}), 404
        
    try:
        # Read current content
        with open(dotenv_path, "r") as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            replaced = False
            for key, val in data.items():
                if line.strip().startswith(f"{key}="):
                    new_lines.append(f"{key}={val}\n")
                    replaced = True
                    break
            if not replaced:
                new_lines.append(line)
                
        # Write back updated configs
        with open(dotenv_path, "w") as f:
            f.writelines(new_lines)
            
        return jsonify({"success": True, "message": "Configuration saved successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error saving configuration: {str(e)}"}), 500

@app.route("/output/<path:filename>")
def serve_output(filename):
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    return send_from_directory(output_dir, filename)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VEO SHORTS | Cinematic Faceless AI Producer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #07090e;
            --bg-card: #0d111a;
            --accent-glow: #e040fb; /* Neon Violet */
            --accent-secondary: #00e5ff; /* Cyan */
            --accent-veo: #ff1744; /* Vivid Red */
            --text-main: #f3f4f6;
            --text-dim: #9ca3af;
            --border-glass: rgba(255, 255, 255, 0.08);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Sidebar Navigation */
        aside {
            width: 320px;
            background-color: #0b0e14;
            border-right: 1px solid var(--border-glass);
            padding: 2.5rem 2rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100vh;
        }

        .logo {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .logo-main {
            font-size: 1.80rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent-glow) 0%, var(--accent-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
        }

        .logo-sub {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-dim);
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .config-section {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            margin-top: 2rem;
            flex: 1;
            overflow-y: auto;
            padding-right: 4px;
        }

        .config-title {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-dim);
            border-bottom: 1px solid var(--border-glass);
            padding-bottom: 6px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .input-group label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-dim);
        }

        .input-group input, .input-group select {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-glass);
            border-radius: 10px;
            padding: 10px 14px;
            color: var(--text-main);
            font-size: 0.9rem;
            outline: none;
            transition: var(--transition);
        }

        .input-group input:focus, .input-group select:focus {
            border-color: var(--accent-secondary);
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.15);
        }

        .btn-save {
            background: linear-gradient(135deg, var(--accent-glow) 0%, var(--accent-secondary) 100%);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 1rem;
        }

        .btn-save:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(224, 64, 251, 0.3);
        }

        /* Main Workspace */
        main {
            flex: 1;
            padding: 2.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            height: 100vh;
            overflow-y: auto;
        }

        /* Top Bar */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-title h1 {
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 4px;
        }

        .header-title p {
            color: var(--text-dim);
        }

        .btn-trigger {
            background: linear-gradient(135deg, var(--accent-veo) 0%, #ff5252 100%);
            color: #fff;
            border: none;
            border-radius: 50px;
            padding: 14px 30px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 10px 25px rgba(255, 23, 68, 0.3);
        }

        .btn-trigger:hover:not(:disabled) {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 15px 30px rgba(255, 23, 68, 0.5);
        }

        .btn-trigger:disabled {
            background: #2b303c;
            color: var(--text-dim);
            box-shadow: none;
            cursor: not-allowed;
        }

        /* Main Dashboard Grid */
        .workspace-grid {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 2rem;
            flex: 1;
            min-height: 0;
        }

        /* Panel Container */
        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            min-height: 0;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-title {
            font-size: 1.15rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Real-time Terminal Logs */
        .terminal {
            background-color: #05070a;
            border-radius: 16px;
            padding: 1.25rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #00ff66; /* Console Green */
            overflow-y: auto;
            flex: 1;
            border: 1px solid rgba(0, 255, 102, 0.15);
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        /* Live Video Preview */
        .video-container {
            background: #05070a;
            border-radius: 16px;
            overflow: hidden;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            aspect-ratio: 9/16;
            max-height: 480px;
            margin: auto;
            border: 1px solid var(--border-glass);
        }

        .video-container video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .no-video {
            text-align: center;
            color: var(--text-dim);
            padding: 2rem;
        }

        .no-video svg {
            width: 64px;
            height: 64px;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.1);
        }

        /* Status & Progress Bar */
        .status-card {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid var(--border-glass);
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .progress-track {
            height: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, var(--accent-glow) 0%, var(--accent-secondary) 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
        }

        /* Animations */
        .pulse {
            animation: pulse-animation 2s infinite;
        }

        @keyframes pulse-animation {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-glass);
            border-radius: 10px;
        }
    </style>
</head>
<body>

    <!-- SIDEBAR: Configurations -->
    <aside>
        <div class="logo">
            <span class="logo-main">VEO SHORTS</span>
            <span class="logo-sub">Faceless AI Producer</span>
        </div>

        <form id="configForm" class="config-section">
            <span class="config-title">Generation Model</span>
            <div class="input-group">
                <label for="useVeo">Google Veo 3.5 Tier</label>
                <select id="useVeo" name="USE_VEO">
                    <option value="True" {% if env_vars.get('USE_VEO') == 'True' %}selected{% endif %}>ACTIVE (Premium Video)</option>
                    <option value="False" {% if env_vars.get('USE_VEO') != 'True' %}selected{% endif %}>INACTIVE (Flux Image)</option>
                </select>
            </div>

            <span class="config-title">API Integration Keys</span>
            <div class="input-group">
                <label for="googleKey">Google AI Studio Key</label>
                <input type="password" id="googleKey" name="GOOGLE_API_KEY" value="{{ env_vars.get('GOOGLE_API_KEY', '') }}" placeholder="AIzaSy...">
            </div>

            <span class="config-title">YouTube Automation</span>
            <div class="input-group">
                <label for="uploadEnabled">Auto-Upload to Channel</label>
                <select id="uploadEnabled" name="UPLOAD_ENABLED">
                    <option value="True" {% if env_vars.get('UPLOAD_ENABLED') == 'True' %}selected{% endif %}>ENABLED</option>
                    <option value="False" {% if env_vars.get('UPLOAD_ENABLED') != 'True' %}selected{% endif %}>DISABLED</option>
                </select>
            </div>

            <div class="input-group">
                <label for="channelId">YouTube Channel ID</label>
                <input type="text" id="channelId" name="YOUTUBE_CHANNEL_ID" value="{{ env_vars.get('YOUTUBE_CHANNEL_ID', '') }}" placeholder="UC...">
            </div>

            <span class="config-title">Email Alerts</span>
            <div class="input-group">
                <label for="emailSender">Recipient Email</label>
                <input type="text" id="emailSender" name="EMAIL_SENDER" value="{{ env_vars.get('EMAIL_SENDER', '') }}" placeholder="name@domain.com">
            </div>

            <button type="submit" class="btn-save">Save Configurations</button>
        </form>

        <div style="font-size: 0.75rem; color: var(--text-dim); text-align: center; border-top: 1px solid var(--border-glass); padding-top: 15px;">
            Secured Connection • Port 5001
        </div>
    </aside>

    <!-- MAIN DASHBOARD -->
    <main>
        <div class="topbar">
            <div class="header-title">
                <h1>AI Studio Workspace</h1>
                <p>Monitor your autonomous video creation, Google Veo compilation, and retention-captions rendering in real-time.</p>
            </div>
            <button class="btn-trigger" id="btnTrigger" onclick="startGeneration()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                Launch Production
            </button>
        </div>

        <div class="workspace-grid">
            <!-- Left Panel: Log Monitor -->
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-title">
                        <span style="width: 10px; height: 10px; border-radius: 50%; background: #00ff66; display: inline-block;" class="pulse" id="statusDot"></span>
                        Real-time Process Terminal
                    </span>
                    <span id="elapsedTime" style="font-size: 0.9rem; font-family: monospace; color: var(--text-dim);">Elapsed: 0s</span>
                </div>

                <div class="terminal" id="terminal">
                    <div>> Console idle. Click "Launch Production" to start generation.</div>
                </div>

                <div class="status-card">
                    <div class="progress-header">
                        <span id="progressText">System Status: Idle</span>
                        <span id="progressPercent">0%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                </div>
            </div>

            <!-- Right Panel: Video Preview -->
            <div class="panel" style="justify-content: center;">
                <div class="panel-header" style="flex: 0 0 auto;">
                    <span class="panel-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
                        Compiled Short Preview
                    </span>
                </div>

                <div class="video-container" id="videoContainer">
                    <div class="no-video">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
                        <p style="font-weight: 600;">No Preview Available</p>
                        <p style="font-size: 0.8rem; margin-top: 4px;">Start a production run to generate a video.</p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Track elapsed time
        let elapsedInterval = null;
        let pollingInterval = null;

        // Check if video is already available
        function checkExistingVideo() {
            fetch('/output/final_video.mp4', { method: 'HEAD' })
                .then(res => {
                    if (res.status === 200) {
                        displayVideo();
                    }
                });
        }

        function displayVideo() {
            const container = document.getElementById('videoContainer');
            // Cache bust the video URL to avoid browser cache issues
            container.innerHTML = `
                <video controls autoplay loop>
                    <source src="/output/final_video.mp4?t=${Date.now()}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            `;
        }

        // Configuration saving
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = {};
            formData.forEach((val, key) => { data[key] = val; });

            fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
            })
            .catch(err => alert("Error saving configuration: " + err));
        });

        function startGeneration() {
            document.getElementById('btnTrigger').disabled = true;
            document.getElementById('statusDot').style.background = '#ff0055';
            
            fetch('/api/start', { method: 'POST' })
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        startStatusPolling();
                    } else {
                        alert(res.message);
                        document.getElementById('btnTrigger').disabled = false;
                    }
                })
                .catch(err => {
                    alert("Error starting production: " + err);
                    document.getElementById('btnTrigger').disabled = false;
                });
        }

        function startStatusPolling() {
            if (pollingInterval) clearInterval(pollingInterval);
            
            pollingInterval = setInterval(() => {
                fetch('/api/status')
                    .then(res => res.json())
                    .then(data => {
                        // Update Elapsed Time
                        document.getElementById('elapsedTime').innerText = `Elapsed: ${data.elapsed}s`;
                        
                        // Update Progress Bar
                        document.getElementById('progressBar').style.width = `${data.progress}%`;
                        document.getElementById('progressPercent').innerText = `${data.progress}%`;
                        
                        // Update status message based on progress
                        let statusText = "System Status: Processing...";
                        if (data.progress >= 95) statusText = "System Status: Uploading & Notifying...";
                        else if (data.progress >= 80) statusText = "System Status: Compiling Subtitles & Audio...";
                        else if (data.progress >= 60) statusText = "System Status: Fetching Scene Assets...";
                        else if (data.progress >= 40) statusText = "System Status: Writing Engaging Video Script...";
                        else if (data.progress >= 25) statusText = "System Status: Pulling Viral Trends...";
                        else if (data.progress === 100) statusText = "System Status: Idle / Finished";
                        
                        document.getElementById('progressText').innerText = statusText;

                        // Update Terminal Logs
                        const terminal = document.getElementById('terminal');
                        if (data.logs.length > 0) {
                            terminal.innerHTML = data.logs.map(log => `<div>> ${log}</div>`).join('');
                            // Scroll to bottom
                            terminal.scrollTop = terminal.scrollHeight;
                        }

                        // Handle finished state
                        if (!data.running) {
                            clearInterval(pollingInterval);
                            document.getElementById('btnTrigger').disabled = false;
                            document.getElementById('statusDot').style.background = '#00ff66';
                            
                            // Check if final_video.mp4 exists now and display it
                            checkExistingVideo();
                        }
                    });
            }, 1500);
        }

        // Initialize state check on page load
        window.addEventListener('load', () => {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    if (data.running) {
                        document.getElementById('btnTrigger').disabled = true;
                        startStatusPolling();
                    } else {
                        checkExistingVideo();
                    }
                });
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
