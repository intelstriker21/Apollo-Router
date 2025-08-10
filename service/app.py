from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import secrets
import psutil
import platform
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
PORTS_FILE = 'ports.txt'
USERNAME = 'admin'  # Default Username
PASSWORD = 'admin'  # Default Password
ROUTER_IP = '0.0.0.0'  # Router IP
MODEL = 'Apollo'  # Router Model
FIRMWARE = '1.0-Beta'  # Firmware Version
MEMORY = '3.83GB'  # Router Memory

# Fetch RAM dynamically (unchanged from previous)
def get_ram_info():
    try:
        total_memory = psutil.virtual_memory().total
        total_memory_gb = total_memory / (1024 ** 3)  # Convert bytes to GB
        return f"{total_memory_gb:.2f}GB"
    except Exception:
        return '3.83GB'  # Fallback to provided value

# Fetch CPU dynamically
def get_cpu_info():
    try:
        # Try parsing /proc/cpuinfo for Linux-based systems (RouterOS compatible)
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        # Extract model name using regex
        match = re.search(r'model name\s*:\s*(.+)', cpuinfo)
        if match:
            cpu_name = match.group(1).strip()
            # Clean up common redundant info (e.g., "Intel(R) Core(TM)")
            cpu_name = re.sub(r'Intel\(R\)\s*Core\(TM\)\s*', '', cpu_name)
            cpu_name = re.sub(r'\s*CPU\s*', '', cpu_name).strip()
            return cpu_name if cpu_name else 'Unknown CPU'
        # Fallback to psutil if /proc/cpuinfo doesn't provide model name
        cpu_info = platform.processor() or psutil.cpu_info()[0].model_name
        return cpu_info if cpu_info else 'Unknown CPU'
    except Exception:
        return 'Unknown CPU'  # Fallback value

RAM = get_ram_info()  # Dynamically fetch RAM
CPU = get_cpu_info()  # Dynamically fetch CPU

if not os.path.exists(PORTS_FILE):
    with open(PORTS_FILE, 'w') as f:
        pass

def add_port(router_port, target_port, ip):
    try:
        os.system(f"socat TCP-LISTEN:{router_port},fork,reuseaddr TCP:{ip}:{target_port} &")
        with open(PORTS_FILE, 'a') as f:
            f.write(f"{router_port},{target_port},{ip}\n")
        return True
    except Exception:
        return False

def read_ports():
    with open(PORTS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def format_ports(ports):
    return [f"{p.split(',')[2]}:{p.split(',')[1]} <- Router -> {ROUTER_IP}:{p.split(',')[0]}" for p in ports]

@app.route('/remove_port', methods=['GET', 'POST'])
def remove_port_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        router_port = request.form['port']
        ports = [p.split(',')[0] for p in read_ports()]
        if router_port in ports:
            if remove_port(router_port):
                flash(f"Router Port {router_port} removed successfully!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(f"Failed to remove Router Port {router_port}", 'danger')
        else:
            flash(f"Router Port {router_port} not found", 'danger')
    return render_template('remove_port.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('info_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password and new_password == confirm_password:
            global PASSWORD
            PASSWORD = new_password
            flash('Password reset successfully!', 'success')
            return redirect(url_for('info_dashboard'))
        else:
            flash('Passwords do not match. Try again.', 'danger')
    return render_template('reset_password.html')

@app.route('/info_dashboard')
def info_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    ports = read_ports()
    return render_template('info_dashboard.html',
                           ports_count=len(ports),
                           ip=ROUTER_IP,
                           model=MODEL,
                           firmware=FIRMWARE,
                           cpu=CPU,
                           memory=MEMORY)

@app.route('/add_port', methods=['GET', 'POST'])
def add_port_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        router_port = request.form['router_port']
        target_port = request.form['target_port']
        ip = request.form['ip']
        if router_port.isdigit() and target_port.isdigit() and ip:
            if add_port(router_port, target_port, ip):
                flash(f"Router Port {router_port} -> {ip}:{target_port} added successfully!", 'success')
                return redirect(url_for('info_dashboard'))
            else:
                flash(f"Failed to add port {router_port} -> {ip}:{target_port}", 'danger')
        else:
            flash("Invalid port numbers or IP", 'danger')
    return render_template('add_port.html')

def remove_port(router_port):
    try:
        os.system(f"pkill -f 'socat TCP-LISTEN:{router_port}'")
        ports = read_ports()
        ports = [p for p in ports if not p.startswith(router_port)]
        with open(PORTS_FILE, 'w') as f:
            f.writelines(f"{p}\n" for p in ports)
        return True
    except Exception:
        return False

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    ports = format_ports(read_ports())[::-1]
    return render_template('dashboard.html', ports=ports)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def start_all_ports():
    for line in read_ports():
        if line.strip():
            router_port, target_port, ip = line.split(',')
            os.system(f"socat TCP-LISTEN:{router_port},fork,reuseaddr TCP:{ip}:{target_port} &")

if __name__ == '__main__':
    start_all_ports()
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'cert.key'), debug=True)
