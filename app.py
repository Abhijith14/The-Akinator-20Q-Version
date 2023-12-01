# app.py
from flask import Flask, render_template, request, jsonify
import requests

from config import API_KEY as candidate_api_key, PROXY_URL as llm_proxy_url, Question_limit as question_limit

app = Flask(__name__)


question_count = 0

# Set headers with the x-api-key
headers = {
    "x-api-key": candidate_api_key
}


data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user", 
            "content": "Let's play a guessing game. I will think of an object and you have to guess what it is by asking yes or no questions. You only get {0} questions total. Please ask one question at a time and wait for my response of 'yes' or 'no' before asking the next question. If you do not guess correctly in {0} or fewer questions, you should apologize for losing the game and ask if I would like to play again with a new object. You will start the game by asking your first yes or no question to narrow down what I am thinking of. Begin when ready.".format(question_limit)
        }
    ]
}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/game')
def start_game():
    return render_template('game.html')


@app.route('/get_question', methods=['POST'])
def get_question():
    global question_count
    question_count += 1

    question = request.json.get("question", "")

    if question_count <= question_limit:
        answer = get_llm_answer(question, question_count)
        return jsonify({"question": str(answer), "reset": False})
    
    else:
        question_count = 0
        reset()
        return jsonify({"question": "Game ended.", "reset": True})



# get the answer from the LLM
def get_llm_answer(question, question_count):
    global data, headers
    if question_count == 1:
        response = requests.post(llm_proxy_url, json=data, headers=headers)
        answer = response.json()["choices"][0]['message']['content']
        data["messages"].append({"role": "assistant", "content": answer})
    else:
        data["messages"].append({"role": "user", "content": question})
        response = requests.post(llm_proxy_url, json=data, headers=headers)
        answer = response.json()["choices"][0]['message']['content']
        data["messages"].append({"role": "assistant", "content": answer})

    return answer



# reset the question limit
def reset():
    global question_count, data
    question_count = 0
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user", 
                "content": "Let's play a guessing game. I will think of an object and you have to guess what it is by asking yes or no questions. You only get 5 questions total. Please ask one question at a time and wait for my response of 'yes' or 'no' before asking the next question. If you do not guess correctly in 5 or fewer questions, you should apologize for losing the game and ask if I would like to play again with a new object. You will start the game by asking your first yes or no question to narrow down what I am thinking of. Begin when ready."
            }
        ]
    }
    

if __name__ == '__main__':
    app.run(debug=True)
