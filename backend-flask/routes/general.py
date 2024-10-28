def load(app):
    @app.route('/api/health')
    def health_check():
        return {'success': True}, 200