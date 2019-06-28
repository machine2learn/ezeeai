import webbrowser
from threading import Timer
from ezeeai.dfweb import app, appConfig


def open_browser():
    webbrowser.open_new('http://localhost:5000')


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=False,
            threaded=True,
            host=appConfig.host(),
            port=appConfig.port())
