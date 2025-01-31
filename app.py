from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import docker
import random
import subprocess
import time
import json
import os
import uuid
from threading import Thread

app = Flask(__name__)
app.secret_key = os.urandom(24)
client = docker.from_env()

# Archivos de datos
ACCOUNTS_FILE = 'accounts.json'
CONTAINERS_FILE = 'containers.json'

def load_data(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

accounts = load_data(ACCOUNTS_FILE)
containers = load_data(CONTAINERS_FILE)

def cleanup_containers():
    while True:
        try:
            current_time = time.time()
            for cid, data in list(containers.items()):
                # Contenedores anónimos: 1 hora
                if 'username' not in data and current_time - data['created_at'] > 3600:
                    remove_container(cid)
                
                # Contenedores registrados: 24h de inactividad
                elif 'username' in data:
                    user_data = accounts.get(data['username'], {})
                    last_active = user_data.get('last_active', 0)
                    if current_time - last_active > 86400:
                        remove_container(cid)
            
            time.sleep(300)
            
        except Exception as e:
            print(f"Error en limpieza: {str(e)}")

def remove_container(cid):
    try:
        container = client.containers.get(cid)
        container.stop(timeout=1)
        container.remove()
    except:
        pass
    del containers[cid]
    save_data(containers, CONTAINERS_FILE)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    elif 'guest_id' in session:
        return render_template('dashboard.html', username=None)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in accounts:
            return "Usuario ya existe", 400
            
        accounts[username] = {
            'password': generate_password_hash(password),
            'created_at': time.time(),
            'last_active': time.time()
        }
        
        save_data(accounts, ACCOUNTS_FILE)
        session['username'] = username
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in accounts and check_password_hash(accounts[username]['password'], password):
            session['username'] = username
            accounts[username]['last_active'] = time.time()
            save_data(accounts, ACCOUNTS_FILE)
            return redirect(url_for('index'))
            
        return "Credenciales inválidas", 401
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('guest_id', None)
    return redirect(url_for('index'))

@app.route('/create-vps', methods=['POST'])
def create_vps():
    # Para usuarios autenticados
    if 'username' in session:
        username = session['username']
        for cid, data in containers.items():
            if data.get('username') == username:
                return jsonify({
                    'status': 'success',
                    'terminal_url': f"/terminal/{cid}"
                })
    
    # Para usuarios anónimos
    if 'guest_id' not in session:
        session['guest_id'] = str(uuid.uuid4())
    
    guest_id = session['guest_id']
    
    try:
        port = random.randint(10000, 20000)
        container = client.containers.run(
            "ubuntu:latest",
            detach=True,
            tty=True,
            stdin_open=True,
            command="/bin/bash -c 'apt update && apt install -y sudo nano wget curl screen && tail -f /dev/null'"
        )
        
        ttyd_cmd = f"ttyd -p {port} -W -t fontSize=14 docker exec -it {container.id} /bin/bash"
        subprocess.Popen(ttyd_cmd, shell=True)
        
        container_data = {
            'port': port,
            'created_at': time.time()
        }
        
        if 'username' in session:
            container_data['username'] = session['username']
            accounts[session['username']]['last_active'] = time.time()
        else:
            container_data['guest_id'] = guest_id
        
        containers[container.id] = container_data
        save_data(containers, CONTAINERS_FILE)
        save_data(accounts, ACCOUNTS_FILE)
        
        return jsonify({
            'status': 'success',
            'terminal_url': f"/terminal/{container.id}"
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/terminal/<cid>')
def terminal(cid):
    container_data = containers.get(cid)
    if not container_data:
        return "Contenedor no encontrado", 404
    
    # Verificar permisos
    if 'username' in session:
        if container_data.get('username') == session['username']:
            accounts[session['username']]['last_active'] = time.time()
            save_data(accounts, ACCOUNTS_FILE)
            return render_template('terminal.html', port=container_data['port'])
    
    elif 'guest_id' in session and container_data.get('guest_id') == session['guest_id']:
        return render_template('terminal.html', port=container_data['port'])
    
    return "Acceso no autorizado", 403

if __name__ == '__main__':
    Thread(target=cleanup_containers, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
