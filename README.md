# KVM-Router

KVM-Router is a lightweight, web-based router management tool designed for VPS/Locked-Down environments. With features like port forwarding, Tailscale integration (Not via UI), and the ability to function as a Tailscale exit node, it provides flexibility and control over your network.

## Features

- **Port Management**: Easily add and remove port forwarding rules through a web interface.
- **Tailscale Integration**: Use your Router/Host/VPS as a Tailscale exit node for public access to local resources with an public-ipv4 router (GCNAT)
- **Router Info Dashboard**: View router information, such as IP address, model, firmware, CPU, and memory stats.
- **Password Management**: Reset the default admin password via the web interface.

## Installation

### Requirements

- Python 3.x (Python 3.10 Recommended)
- Flask
- OpenSSL (to generate SSL certificates)
- socat (to port forward)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/katy-the-kat/KVM-Router
   cd KVM-router/service
   ```

2. Install dependencies:
   ```bash
   pip3 install flask
   ```

3. Generate a self-signed SSL certificate:
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.key -out cert.pem
   ```

4. Run the application:
   ```bash
   python3 app.py
   ```

5. Access the application in your browser at `https://<your-server-ip>` (default port: 443).

## Default Login Credentials

- Username: `admin`
- Password: `password`

## Configuration

- Edit the following variables in `main.py` to match your setup:
  ```python
  ROUTER_IP = '0.0.0.0'  # Router IP
  MODEL = 'M1'           # Router Model
  RAM = '1GB'            # Router RAM Size
  CPU = 'Intel Atom'     # Router CPU
  USERNAME = 'admin'     # Default Username, Please Change.
  PASSWORD = 'password'  # Default Password, Please Change.
  ```

## File Structure

- `app.py`: Main application file containing the backend logic.
- `templates/`: Directory containing HTML + CSS templates for the web interface.
- `ports.txt`: File used to store port forwarding rules.

## Usage

### Port Forwarding

1. **Add a Port**:
   - Navigate to the "Add Port" page.
   - Enter the `Router Port`, `Target Port`, and `IP Address` of the target device.
   - Submit the form to add the port forwarding rule.

2. **Remove a Port**:
   - Go to the "Remove Port" page.
   - Enter the `Router Port` to remove.
   - Submit the form to delete the port forwarding rule.

3. **View Active Ports**:
   - Visit the "Port Dashboard" to see all active port forwarding rules.

### Resetting Password

- Access the "Reset Password" page from the dashboard.
- Enter and confirm your new password.

### Viewing Router Info

- Navigate to the "Info Dashboard" to view:
  - Router IP address
  - Active ports count
  - Router model
  - Firmware version
  - CPU and memory specs

## Notes

- By default, the application runs on port 443 using HTTPS.
- The router uses `socat` for port forwarding. Ensure `socat` is installed on your server.
- Tailscale integration allows a Host/VPS to act as an exit node or connect to your local network to a public ipv4 address.

## Contributing

Feel free to submit pull requests or issues to improve KVM-Router. Contributions are always welcome!

## Acknowledgments

- Created by `discord.gg/dell`.
- Powered by Flask and Socat.
