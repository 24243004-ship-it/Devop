
from flask import Flask, render_template_string, redirect, url_for, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Python Counter App</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #eef2ff;
            color: #1e293b;
            margin: 0;
            padding: 25px;
        }

        h1 {
            text-align: center;
            color: #4338ca;
        }

        .pipeline {
            max-width: 750px;
            margin: 20px auto;
            padding: 16px;
            background: #e0e7ff;
            border-radius: 10px;
            text-align: center;
            line-height: 2;
        }

        .card {
            background: white;
            max-width: 430px;
            margin: 25px auto;
            padding: 30px;
            text-align: center;
            border-radius: 15px;
            box-shadow: 0 5px 20px #00000012;
        }

        .count {
            font-size: 65px;
            font-weight: bold;
            color: #4338ca;
            margin: 25px 0;
        }

        .buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }

        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 16px;
            min-width: 95px;
        }

        button:hover {
            opacity: 0.85;
        }

        .increment {
            background: #16a34a;
        }

        .decrement {
            background: #dc2626;
        }

        .reset {
            background: #4338ca;
        }

        .status {
            margin-top: 22px;
            color: #64748b;
        }

        .pipeline-title {
            font-weight: bold;
        }
    </style>
</head>

<body>
    <h1>Python Counter App</h1>

    <div class="pipeline">
        <div class="pipeline-title">COUNTER PIPELINE</div>
        User Action → Process Request → Update Counter → Display Result
    </div>

    <div class="card">
        <h2>Counter</h2>

        <div class="count">{{ count }}</div>

        <div class="buttons">
            <form method="POST" action="/decrement">
                <button class="decrement" type="submit">− Decrement</button>
            </form>

            <form method="POST" action="/increment">
                <button class="increment" type="submit">+ Increment</button>
            </form>
        </div>

        <form method="POST" action="/reset" style="margin-top: 15px;">
            <button class="reset" type="submit">Reset Counter</button>
        </form>

        <div class="status">
            Status: {{ status }}
        </div>
    </div>
</body>
</html>
"""


def get_count():
    value = session.get("count", 0)

    if not isinstance(value, int):
        value = 0
        session["count"] = value

    return value


@app.route("/")
def home():
    count = get_count()

    if count > 0:
        status = "Counter is positive"
    elif count < 0:
        status = "Counter is negative"
    else:
        status = "Counter is zero"

    return render_template_string(
        HTML,
        count=count,
        status=status
    )


@app.route("/increment", methods=["POST"])
def increment():
    session["count"] = get_count() + 1
    return redirect(url_for("home"))


@app.route("/decrement", methods=["POST"])
def decrement():
    session["count"] = get_count() - 1
    return redirect(url_for("home"))


@app.route("/reset", methods=["POST"])
def reset():
    session["count"] = 0
    return redirect(url_for("home"))


if __name__ == "__main__":
    print("Counter App started successfully!")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=False)
