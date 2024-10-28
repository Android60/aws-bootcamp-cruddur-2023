def load(app):
    @app.route('/api/health')
    def health_check():
        return {'success': True}, 200

    # @app.route('/rollbar/test')
    # def rollbar_test():
    #     rollbar.report_message('Hello World!', 'warning')
    #     return "Hello World!"