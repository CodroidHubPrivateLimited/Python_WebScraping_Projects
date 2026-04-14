import flask

app = flask.Flask(__name__)

print("Hello world!")

print(dir(flask))

@app.route("/")
def index():
  return flask.render_template("index.html")

if __name__ == "__main__":
  app.run(port=5000, debug=True)
