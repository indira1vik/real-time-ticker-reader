from flask import Flask, render_template, request
import subprocess
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", name = "Indira")

@app.route("/submit", methods = ['GET', 'POST'])
def submit():
    if request.method == 'POST':
        url_input = str(request.form['url_input'])
        if url_input == "":
            return render_template("streaming.html", url_input = url_input)
        elif url_input == "Camera":
            command = ["python", "play.py", "-c"]
        elif url_input.startswith("https"):
            command = ["python", "play.py", "-v", url_input]
        elif url_input.startswith("./") or url_input.startswith("/") or url_input.startswith("E"):
            command = ["python", "play.py", "-r", url_input]
        else:
            return render_template("streaming.html", url_input = url_input)

    output_lines = []
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as process:
        for line in process.stdout:
            output_lines.append(line.strip())
    return render_template("streaming.html", url_input = url_input, output_lines=output_lines)

if __name__ == '__main__':
    app.run(debug=True,port=8087)