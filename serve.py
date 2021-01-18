#!/usr/bin/python3
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def new_event():
    print(request.json)
    return request.json

def challenge():
    _token = request.json.get('token', '')
    _challenge = request.json.get('challenge', '')
    _type = request.json.get('type', '')
    signing_secret = "daca389b212fd98dab4bc50df92873c7"
    verifier = SignatureVerifier(signing_secret)
    timestamp = request.headers['X-Slack-Request-Timestamp']
    signature = verifier.generate_signature(
        timestamp=timestamp, body=request.json
    )
    return _challenge

if __name__ == '__main__':
    app.run(debug=True)
