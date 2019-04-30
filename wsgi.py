from easyai.dfweb import app, appConfig

if __name__ == "__main__":
    app.run(debug=appConfig.debug(),
            threaded=appConfig.threaded(),
            host=appConfig.host(),
            port=appConfig.port())
