from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
from blockchain import Blockchain


app = Flask(__name__)
app.secret_key = 'soumya_secret_key'  # Replace with a strong key in production
blockchain = Blockchain()

# Load user data
def load_users():
    if not os.path.exists('users.json'):
        # Create the file with empty data if not exists
        with open('users.json', 'w') as f:
            json.dump({}, f)
    with open('users.json', 'r') as f:
        return json.load(f)
# Save user data
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users:
            return "Username already exists!"
        users[username] = {"password": password, "role": "voter"}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    username = session['username']
    if users.get(username, {}).get('voted', False):
        return "You have already voted."

    candidates = ['Vicky', 'Yogesh', 'Ritk']  # Add your real candidates here

    if request.method == 'POST':
        candidate = request.form.get('candidate')
        if not candidate:
            return "No candidate selected", 400

        # ✅ Mark as voted BEFORE blockchain changes
        users[username]['voted'] = True
        save_users(users)

        # ✅ Add vote to blockchain
        blockchain.add_new_vote(username, candidate)
        blockchain.mine()

        return redirect(url_for('results'))

    return render_template('vote.html', candidates=candidates)



@app.route('/results')
def results():
    if not session.get('is_admin'):
        return redirect('/admin')

    vote_counts = {}
    for block in blockchain.chain:
        if 'data' in block:
            candidate = block['data'].get('candidate')
            if candidate:
                vote_counts[candidate] = vote_counts.get(candidate, 0) + 1

    return render_template('results.html', results=vote_counts)



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            return redirect('/dashboard')
        else:
            return "Invalid admin credentials"
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect('/admin')

    import json
    with open('users.json', 'r') as f:
        users_dict = json.load(f)
    users = []
    for username, info in users_dict.items():
        user_obj = info.copy()
        user_obj['username'] = username
        users.append(user_obj)
    blocks = json.dumps(blockchain.chain, indent=4)

    return render_template('dashboard.html', users=users, blocks=blocks)



@app.route('/logout')
def logout():
    session.clear()  
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
