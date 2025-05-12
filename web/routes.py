from flask import render_template, redirect, url_for, request, flash
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
import json

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Generate a new wallet for the voter
            wallet = Wallet()
            private_key = wallet.private_key
            public_key = wallet.public_key
            
            # Register the voter
            if app.blockchain.register_voter(public_key):
                flash('Registration successful! Save your credentials.', 'success')
                return render_template('register.html', 
                                    registered=True, 
                                    private_key=private_key,
                                    public_key=public_key)
            else:
                flash('Registration failed. This voter may already be registered.', 'danger')
        
        return render_template('register.html', registered=False)

    @app.route('/vote', methods=['GET', 'POST'])
    def vote():
        candidates = ["Candidate A", "Candidate B", "Candidate C"]  # Example candidates
        
        if request.method == 'POST':
            private_key = request.form.get('private_key')
            selected_candidate = request.form.get('candidate')
            
            try:
                # Create a wallet with the provided private key
                wallet = Wallet()
                wallet.private_key = private_key
                wallet.generate_public_key()
                
                # Create and sign a transaction
                transaction = Transaction(
                    sender=wallet.public_key,
                    recipient="ELECTION",
                    data={"vote": selected_candidate}
                )
                transaction.sign_transaction(wallet)
                
                # Add the transaction to the blockchain
                if app.blockchain.add_transaction(transaction):
                    flash('Vote cast successfully!', 'success')
                    return redirect(url_for('results'))
                else:
                    flash('Failed to cast vote. You may have already voted or not be registered.', 'danger')
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
        
        return render_template('vote.html', candidates=candidates)

    @app.route('/results')
    def results():
        # Count votes from the blockchain
        vote_counts = {}
        
        for block in app.blockchain.chain:
            for transaction in block.transactions:
                if transaction.recipient == "ELECTION" and "vote" in transaction.data:
                    candidate = transaction.data["vote"]
                    if candidate in vote_counts:
                        vote_counts[candidate] += 1
                    else:
                        vote_counts[candidate] = 1
        
        return render_template('results.html', results=vote_counts)

    @app.route('/mine')
    def mine():
        # Mine pending transactions
        miner_address = "SYSTEM"
        mined_block = app.blockchain.mine_pending_transactions(miner_address)
        
        flash(f'Block mined! Hash: {mined_block.hash[:10]}...', 'success')
        return redirect(url_for('results'))
