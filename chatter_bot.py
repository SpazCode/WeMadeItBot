from chatter_bot import ChatBot
import sys
chatbot = ChatBot("BlackWhitby", logic_adapter="chatterbot.adapters.logic.ClosestMatchAdapter")
chatbot.train("chatterbot.corpus.english")

conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

chatbot.train(conversation)

going = True
while going:
    message = raw_input(': ')
    res = chatbot.get_response(str(message))
    print(res)