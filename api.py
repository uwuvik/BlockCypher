def render_transaction_page(txid, amount, receiving_address):
    """Generate transaction page HTML with dynamic content"""
    
    # Read the template file
    try:
        with open('ltc/tx/goo9htrad6r7krkkr05zmqro33fm63bcie.html', 'r') as f:
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

    # Add dynamic confirmation and time update script
    confirmation_script = f'''
    <script>
    const txId = '{txid}';
    const maxConfirmations = 6;
    
    // Get stored confirmation count or start at 0
    let currentConfirmations = parseInt(localStorage.getItem('confirmations_' + txId) || '0');
    
    // Get stored start time or use current time
    const startTimeKey = 'startTime_' + txId;
    let startTime = localStorage.getItem(startTimeKey);
    if (!startTime) {{
        startTime = Date.now();
        localStorage.setItem(startTimeKey, startTime);
    }} else {{
        startTime = parseInt(startTime);
    }}

    function formatTimeAgo(minutes) {{
        if (minutes === 0) {{
            return "a few seconds ago";
        }} else if (minutes === 1) {{
            return "1 minute ago";
        }} else if (minutes < 60) {{
            return minutes + " minutes ago";
        }} else {{
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;

            if (hours === 1 && remainingMinutes === 0) {{
                return "1 hour ago";
            }} else if (hours === 1) {{
                return "1 hour, " + remainingMinutes + " minute" + (remainingMinutes === 1 ? "" : "s") + " ago";
            }} else if (remainingMinutes === 0) {{
                return hours + " hours ago";
            }} else {{
                return hours + " hours, " + remainingMinutes + " minute" + (remainingMinutes === 1 ? "" : "s") + " ago";
            }}
        }}
    }}

    function updateTime() {{
        const timeElement = document.querySelector('time.timeago');
        if (timeElement) {{
            const now = Date.now();
            const elapsedMinutes = Math.floor((now - startTime) / (1000 * 60));
            timeElement.textContent = formatTimeAgo(elapsedMinutes);
        }}
    }}

    function updateConfirmations() {{
        const confSection = document.getElementById('conf-section');
        const numConfs = document.getElementById('num-confs');
        const lockIcon = confSection.querySelector('i');

        if (currentConfirmations < maxConfirmations) {{
            currentConfirmations++;
            localStorage.setItem('confirmations_' + txId, currentConfirmations);
            numConfs.textContent = currentConfirmations + '/6';

            if (currentConfirmations === 1) {{
                // Orange for 1/6
                lockIcon.style.color = '#ff8c00';
                numConfs.style.color = '#ff8c00';
                lockIcon.className = 'fa fa-lock';
            }} else if (currentConfirmations >= 6) {{
                // Green for 6/6 (completed)
                lockIcon.style.color = '#28a745';
                numConfs.style.color = '#28a745';
                lockIcon.className = 'fa fa-unlock';
                confSection.className = 'completed';
            }} else {{
                // Keep orange for 2-5
                lockIcon.style.color = '#ff8c00';
                numConfs.style.color = '#ff8c00';
            }}
        }}
    }}

    function initializeConfirmationDisplay() {{
        const confSection = document.getElementById('conf-section');
        const numConfs = document.getElementById('num-confs');
        const lockIcon = confSection.querySelector('i');
        
        // Update display based on current confirmations
        if (currentConfirmations > 0) {{
            numConfs.textContent = currentConfirmations + '/6';
            
            if (currentConfirmations === 1) {{
                lockIcon.style.color = '#ff8c00';
                numConfs.style.color = '#ff8c00';
                lockIcon.className = 'fa fa-lock';
            }} else if (currentConfirmations >= 6) {{
                lockIcon.style.color = '#28a745';
                numConfs.style.color = '#28a745';
                lockIcon.className = 'fa fa-unlock';
                confSection.className = 'completed';
            }} else {{
                lockIcon.style.color = '#ff8c00';
                numConfs.style.color = '#ff8c00';
            }}
        }}
    }}

    // Initialize displays immediately
    updateTime();
    initializeConfirmationDisplay();

    // Update time every minute (60 seconds)
    setInterval(updateTime, 60000);

    // Check if we should start confirmation progression
    const now = Date.now();
    const elapsedTime = now - startTime;
    const firstConfirmationTime = 90000; // 1.5 minutes
    
    if (currentConfirmations === 0 && elapsedTime >= firstConfirmationTime) {{
        // Immediately show first confirmation if enough time has passed
        updateConfirmations();
    }} else if (currentConfirmations === 0) {{
        // Wait for the remaining time until first confirmation
        const remainingTime = firstConfirmationTime - elapsedTime;
        setTimeout(() => {{
            updateConfirmations();
        }}, remainingTime);
    }}

    // Set up ongoing confirmation updates
    function scheduleNextConfirmation() {{
        if (currentConfirmations >= maxConfirmations) return;
        
        const confirmationInterval = 120000; // 2 minutes
        let nextConfirmationTime;
        
        if (currentConfirmations === 0) {{
            nextConfirmationTime = startTime + firstConfirmationTime;
        }} else {{
            nextConfirmationTime = startTime + firstConfirmationTime + (currentConfirmations * confirmationInterval);
        }}
        
        const timeUntilNext = nextConfirmationTime - now;
        
        if (timeUntilNext <= 0) {{
            // Time has already passed, update immediately
            updateConfirmations();
            scheduleNextConfirmation();
        }} else {{
            // Schedule the next update
            setTimeout(() => {{
                updateConfirmations();
                scheduleNextConfirmation();
            }}, timeUntilNext);
        }}
    }}
    
    scheduleNextConfirmation();
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
            'url': f'/tx/{txid}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tx/<txid>')
def serve_transaction_page(txid):
    """Serve transaction pages dynamically"""
    if txid not in TRANSACTIONS:
        return "Transaction not found", 404
    
    tx_data = TRANSACTIONS[txid]
    html = render_transaction_page(tx_data['txid'], tx_data['amount'], tx_data['address'])
    return html

@app.route('/')
def serve_index():
    """Serve the main index page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Enable CORS for external requests
    from flask import Flask
    app.config['DEBUG'] = False  # Disable debug in production
    app.run(host='0.0.0.0', port=5000, threaded=True)
