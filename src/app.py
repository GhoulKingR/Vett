from flask import Flask, render_template, request, redirect, session
from my_lib.board import (
    add_post,
    setup_board,
    get_posts,
    board_exists,
    get_boards,
    get_description,
    get_creation_time,
    is_board_private,
    get_post_replies,
    add_reply,
)
from my_lib.user import add_user, login_user
from secrets import token_hex


app = Flask(__name__)
app.secret_key = token_hex()

app_name = 'Vett'

@app.get("/")
def index():
    error = request.args.get('error')
    username = session.get('username')
    
    return render_template(
        "index.html",
        error=error,
        app_name=app_name,
        boards=get_boards(),
        username=username
    )

@app.post("/create-board")
def createboard():
    name = request.form.get('name')
    invite_only = 1 if request.form.get('invite-only') != None else 0
    username = session.get('username')
    description = request.form.get('description')

    if username == None:
        return redirect("/")
    
    created, message = setup_board(invite_only, name, username, description)
    if created:
        return redirect(f"/boards/{username}/{name}")
    else:
        return redirect(f"/?error={message}")

@app.get("/boards/<string:user>/<string:name>")
def boards(user, name):
    username = session.get('username')
    error = request.args.get('error')

    if not board_exists(user, name):
        return redirect("/")
    else:
        return render_template(
            'board.html',
            board_name=f'{user}/{name}',
            app_name=app_name,
            posts=get_posts(user, name),
            username=username,
            error=error,
            description=get_description(user, name),
            creation_time=get_creation_time(user, name),
            is_private=is_board_private(user, name),
        )

@app.get("/boards/<string:user>/<string:name>/<int:post_id>/replies")
def replies(user, name, post_id):
    if not board_exists(user, name):
        return ""
    else:
        return render_template(
            'post-replies.html',
            posts=get_post_replies(user, name, post_id),
        )

@app.get("/boards/<string:user>/<string:name>/<int:post_id>/reply")
def reply(user, name, post_id):
    username = session.get('username')
    error = request.args.get('error')

    if not board_exists(user, name):
        return ""
    else:
        return render_template(
            'post-reply.html',
            url=f"/boards/{user}/{name}/{post_id}/reply/go",
            username=username,
            error=error,
        )
    
@app.post("/boards/<string:admin>/<string:name>/<int:post_id>/reply/go")
def make_reply(admin, name, post_id):
    message = request.form['message']
    user = request.form['user']
    real_user = session.get('username')
    if user == 'Anonymous' or user == real_user:
        add_reply(message, user, name, admin, post_id)
        return redirect(f"/boards/{admin}/{name}/{post_id}/replies")
    else:
        return redirect(f"/boards/{admin}/{name}/{post_id}/reply?error=Stop+trying+to+impersonate+someone+💀")

@app.post("/post/<string:admin>/<string:name>")
def post(admin, name):
    message = request.form['message']
    user = request.form['user']
    real_user = session.get('username')
    if user == 'Anonymous' or user == real_user:
        add_post(message, user, name, admin)
        return redirect(f"/boards/{admin}/{name}")
    else:
        return redirect(f"/boards/{admin}/{name}?error=Stop+trying+to+impersonate+someone+💀")

@app.get("/auth/signup")
def signup():
    error = request.args.get('error')
    
    return render_template(
        'auth/signup.html',
        app_name=app_name,
        error=error
    )

@app.post("/auth/signup/go")
def registeruser():
    username = request.form['username']
    password = request.form['password']
    added, message = add_user(username, password)
    if added:
        session['username'] = username
        return redirect('/')
    else:
        return redirect(f'/auth/signup?error={message}')
    
@app.get("/auth/logout")
def signout():
    session.pop('username')
    return redirect('/')

@app.get("/auth/login")
def login():
    error = request.args.get('error')
    
    return render_template(
        'auth/login.html',
        app_name=app_name,
        error=error
    )

@app.post("/auth/login/go")
def loginuser():
    username = request.form['username']
    password = request.form['password']
    logged_in, message = login_user(username, password)
    if logged_in:
        session['username'] = username
        return redirect('/')
    else:
        return redirect(f'/auth/login?error={message}')


if __name__ == "__main__":
    app.run(debug=True)