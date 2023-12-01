# app.py
from flask import Flask, render_template, request, jsonify
import requests

from config import API_KEY as candidate_api_key, PROXY_URL as llm_proxy_url

app = Flask(__name__)


question_limit = 0

# Set headers with the x-api-key
headers = {
    "x-api-key": candidate_api_key
}


data = {
    "model" : "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Ask yes/no question to guess whats in my mind. You can only ask 5 questions. Ask one by one to try to guess it in less than 5 questions. If you cross 5 questions, you lose. Apologise when you lose."}]
}




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask_question', methods=['POST'])
def ask_question():
    global question_limit

    question = request.json.get("question")
    question_limit += 1


    if question_limit <= 30:
        # return jsonify({"question": question})
        answer = get_llm_answer(question, question_limit)

        return jsonify({"question": str(answer)})
    
    else:
        return jsonify({"question": "You have reached the limit of questions"})



# get the answer from the LLM
def get_llm_answer(question, question_limit):
    if question_limit == 1:
        response = requests.post(llm_proxy_url, json=data, headers=headers)
        response_json = response.json()
        answer = response.json()["choices"][0]['message']['content']
        data["messages"].append({"role": "assistant", "content": answer})
    else:
        data["messages"].append({"role": "user", "content": question})
        response = requests.post(llm_proxy_url, json=data, headers=headers)
        response_json = response.json()
        answer = response.json()["choices"][0]['message']['content']
        data["messages"].append({"role": "assistant", "content": answer})

    return answer



# reset the question limit
@app.route('/reset_question_limit', methods=['POST'])
def reset_question_limit():
    global question_limit
    question_limit = 0
    return jsonify({"question": "You have reset the question limit"})



if __name__ == '__main__':
    app.run(debug=True)
