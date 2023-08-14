from flask import Flask, request, render_template, redirect, make_response, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# Key names will store itemes in sessions.
CURRENT_SURVEY_KEY ="current_survey"
RESPONSE_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "RosaLockOut"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_choose_survey_form():
    """Shows choose survey form"""

    return  render_template("choose-survey.html", surveys=surveys)

@app.route("/",methods=["POST"])
def choose_survey():
    """Selects a survey"""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template('already-done.html')
    
    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_start.html",survey=survey)

@app.route("/begin",methods =["POST"])
def survey_start():
    """Clear respones in sessions"""

    session[RESPONSE_KEY] = []

    return redirect("/questions/0")

@app.route("/answer",methods =["POST"])
def handle_question():
    """Saves the response and directs to the next question"""

    choice = request.form['answer']
    text = request.form.get("text","")
    responses = session[RESPONSE_KEY]
    responses.append({"choice": choice, "text": text})
    session[RESPONSE_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")
    
@app.route("/questions/<int:qid>")
def show_questions(qid):
    """Display current questions"""
    responses = session.get(RESPONSE_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        return redirect("/")
    # trys to access question page to soon

    if(len(responses) == len(survey.questions)):
        return redirect("/complete")
    # amswerd all the questions!

    if (len(responses) != qid):
        flash(f"INVALID QUESTION ID:{qid}.")
        return redirect (f"/questions/{len(responses)}")
    # trying to access questions of order!!

    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)

@app. route("/complete")
def complete():
    """SURVEY IS DONE! PROMPT NEW PAGE"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSE_KEY]

    html = render_template("complete.html",survey=survey,responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}","yes",max_age=60)
    return response