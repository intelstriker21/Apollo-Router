# Make sure to get a self-signed ssl cert.
#
# Run this command!
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.key -out cert.pem
#
# It will make the Selfsigned cert
# 
# RouterOS is good when merged with a VPS and tailscale, heck you can even use the server thats hosting routerOS as a tailscale exit node
# Which makes it a router.
#
# Also you may connect the VPS to an exitnode to allow yourself to access local stuff like your own router or stuff
# Without throwing tailscale
#
# By default routeros is on port 443
#
# Login:
# admin:password

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

PORTS_FILE = 'ports.txt'

USERNAME = 'admin' # Default Username
PASSWORD = 'password' # Default Password
ROUTER_IP = '0.0.0.0'  # Put Router IP
MODEL = 'M1'  # Put Router Model
RAM = '1GB'  # Put Router RAM Size
CPU = 'Intel Atom'  # Put Router CPU

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
                           firmware="1.0-RELEASE",
                           cpu=CPU,
                           memory=RAM)

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
