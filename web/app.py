from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Import and register routes with the app
    from web.routes import register_routes
    register_routes(app)
    
    return app

def start_web_server(blockchain, host='0.0.0.0', port=5000):
    app = create_app()
    app.blockchain = blockchain
    app.run(host=host, port=port, debug=True)
