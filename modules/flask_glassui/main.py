from flask import Flask, render_template

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    title = 'Hello world!'
    boxtitle = 'Example title'
    content = '<a href="https://google.com" style="text-decoration: none; color: white;">Test</a>'
    progress_enabled = True
    progress_value = 100
    progress_color = "bg-primary"
    button_left_name = 'Left'
    button_right_name = 'Right'
    button_left_active = True
    button_right_active = True
    action_left = "action_left"
    action_right = "action_right"

    return render_template(
        "index.html",
        title=title,
        boxtitle=boxtitle,
        content=content,
        progress_enabled=progress_enabled,
        progress_value=progress_value,
        progress_color=progress_color,
        button_left_name=button_left_name,
        button_right_name=button_right_name,
        button_left_active=button_left_active,
        button_right_active=button_right_active,
        action_left=action_left,
        action_right=action_right,
    )


@app.route("/action_left")
def action_left():
    print("Left button clicked")
    return 0


@app.route("/action_right")
def action_right():
    print("Right button clicked")
    return 0


if __name__ == "__main__":
    app.run(debug=True)
