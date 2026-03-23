# 1. Install Dependencies
!pip install flask pyngrok flask-sqlalchemy pytz -q

import os
from datetime import datetime
import pytz
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pyngrok import ngrok

# 2. DATABASE
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compliance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
IST = pytz.timezone('Asia/Kolkata')

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), default="India")
    entity_type = db.Column(db.String(50), default="Pvt Ltd")
    tasks = db.relationship('Task', backref='client', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    priority = db.Column(db.String(20), default="Medium")

with app.app_context():
    db.create_all()
    if not Client.query.first():
        c1 = Client(company_name="Acme Corp", country="USA", entity_type="LLC")
        c2 = Client(company_name="Tata Steel", country="India", entity_type="Public Ltd")
        db.session.add_all([c1, c2])
        db.session.commit()

        t1 = Task(client_id=1, title="Annual Filing", category="Tax", due_date=datetime(2023, 12, 31).date(), status="Pending")
        t2 = Task(client_id=2, title="GST Monthly Return", category="GST", due_date=datetime(2026, 4, 20).date(), status="Pending")
        db.session.add_all([t1, t2])
        db.session.commit()

# 3. FRONTEND UI
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>LedgersCFO Compliance Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .overdue { background-color: #ffdce0 !important; border-left: 5px solid #dc3545; }
        .sidebar { height: 100vh; background: #212529; color: white; padding: 20px; }
        .client-link { cursor: pointer; padding: 10px; border-radius: 5px; display: block; color: #adb5bd; text-decoration: none; }
        .client-link:hover, .active-client { background: #343a40; color: white; }
        .stats-card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-light">
<div class="container-fluid">
    <div class="row">
        <div class="col-md-3 sidebar">
            <h4>🏢 Clients</h4>
            <hr>
            <div id="clientList"></div>
        </div>

        <div class="col-md-9 p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 id="selectedClientName">Select a Client</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#taskModal">+ New Task</button>
            </div>

            <div class="row mb-4">
                <div class="col-md-4"><div class="card p-3 stats-card text-center"><h5>Total</h5><h3 id="statTotal">0</h3></div></div>
                <div class="col-md-4"><div class="card p-3 stats-card text-center bg-warning"><h5>Pending</h5><h3 id="statPending">0</h3></div></div>
                <div class="col-md-4"><div class="card p-3 stats-card text-center bg-danger text-white"><h5>Overdue</h5><h3 id="statOverdue">0</h3></div></div>
            </div>

            <div class="card p-3 shadow-sm">
                <table class="table">
                    <thead>
                        <tr><th>Task</th><th>Category</th><th>Due Date</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody id="taskBody"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="taskModal" tabindex="-1">
    <div class="modal-dialog">
        <form id="taskForm" class="modal-content">
            <div class="modal-header"><h5>Add Compliance Task</h5></div>
            <div class="modal-body">
                <input type="hidden" id="formClientId">
                <div class="mb-3"><label>Task Title</label><input type="text" id="t_title" class="form-control" required></div>
                <div class="mb-3"><label>Category</label><select id="t_cat" class="form-control"><option>GST</option><option>Income Tax</option><option>ROC</option></select></div>
                <div class="mb-3"><label>Due Date</label><input type="date" id="t_date" class="form-control" required></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="submit" class="btn btn-primary">Save Task</button>
            </div>
        </form>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    let currentClientId = null;

    async function loadClients() {
        const res = await fetch('/api/clients');
        const clients = await res.json();
        document.getElementById('clientList').innerHTML = clients.map(c =>
            `<a class="client-link" onclick="selectClient(${c.id}, '${c.company_name}')">${c.company_name}</a>`
        ).join('');
    }

    async function selectClient(id, name) {
        currentClientId = id;
        document.getElementById('selectedClientName').innerText = name;
        document.getElementById('formClientId').value = id;
        loadTasks();
    }

    async function loadTasks() {
        if(!currentClientId) return;
        const res = await fetch(`/api/tasks?client_id=${currentClientId}`);
        const data = await res.json();

        // Update Stats
        const today = new Date().toISOString().split('T')[0];
        const pending = data.filter(t => t.status === 'Pending');
        const overdue = pending.filter(t => t.due_date < today);

        document.getElementById('statTotal').innerText = data.length;
        document.getElementById('statPending').innerText = pending.length;
        document.getElementById('statOverdue').innerText = overdue.length;

        document.getElementById('taskBody').innerHTML = data.map(t => {
            const isOverdue = t.status === 'Pending' && t.due_date < today;
            return `<tr class="${isOverdue ? 'overdue' : ''}">
                <td>${t.title}</td>
                <td><span class="badge bg-info text-dark">${t.category}</span></td>
                <td>${t.due_date}</td>
                <td><span class="badge ${t.status==='Completed'?'bg-success':'bg-warning text-dark'}">${t.status}</span></td>
                <td>
                    ${t.status === 'Pending' ? `<button class="btn btn-sm btn-outline-success" onclick="updateStatus(${t.id})">Mark Done</button>` : '✅'}
                </td>
            </tr>`;
        }).join('');
    }

    document.getElementById('taskForm').onsubmit = async (e) => {
        e.preventDefault();
        await fetch('/api/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                client_id: currentClientId,
                title: document.getElementById('t_title').value,
                category: document.getElementById('t_cat').value,
                due_date: document.getElementById('t_date').value
            })
        });
        bootstrap.Modal.getInstance(document.getElementById('taskModal')).hide();
        loadTasks();
    };

    async function updateStatus(id) {
        await fetch(`/api/tasks/${id}`, { method: 'PUT' });
        loadTasks();
    }

    window.onload = loadClients;
</script>
</body>
</html>
"""

# 4. API ENDPOINTS
@app.route('/')
def index(): return render_template_string(HTML_UI)

@app.route('/api/clients')
def get_clients():
    clients = Client.query.all()
    return jsonify([{"id": c.id, "company_name": c.company_name} for c in clients])

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    cid = request.args.get('client_id')
    tasks = Task.query.filter_by(client_id=cid).order_by(Task.due_date.asc()).all()
    return jsonify([{
        "id": t.id, "title": t.title, "category": t.category,
        "due_date": str(t.due_date), "status": t.status
    } for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    new_task = Task(
        client_id=data['client_id'], title=data['title'],
        category=data['category'], due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Success"}), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    task.status = "Completed"
    db.session.commit()
    return jsonify({"message": "Updated"})

# 5. RUN SERVER WITH NGROK
NGROK_TOKEN = "36mSHpSl4DWk4VZO6zTudKO3Piz_2ReYvKNYAz8zPKgUJRMxH"
ngrok.set_auth_token(NGROK_TOKEN)

try:
    public_url = ngrok.connect(5000).public_url
    print(f"Public URL Link: {public_url}")
    app.run(port=5000)
except Exception as e:
    print(f"Error: {e}")
