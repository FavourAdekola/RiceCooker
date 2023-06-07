import random

def handle_response(message) -> str:
    p_message = message.lower()
    match p_message:
        case "hello":
               return 'boop beep'
        case "hi":
            return 'beep boop'
        case "good morning":
            return 'good morning!'
        case other:
            if p_message.find('yesorno') > -1:
                choice = random.choice(['yes','no'])
                if choice == 'yes':
                    return 'https://tenor.com/view/jojo-anime-yes-yes-yes-yeah-its-a-yes-gif-17161748'
                else:
                    return 'https://tenor.com/view/jotaro-kujo-jojo-bizarre-adventure-no-no-no-no-nope-gif-14295799'
            if p_message.find('who asked') > -1:
                return 'https://tenor.com/view/i-asked-meme-gumball-gif-23125464'
            if p_message.find('based') > -1:
                return 'Based? Based on what?'

