from AI import AI

def main():
    chatAI = AI() 
    print(chatAI.askAI())

    while True:
        user_input = input("Пользователь: ")
        if user_input == 'СТОП':
            break
        res = chatAI.askAI(input = user_input)

        print("Бай: "+ res)

if __name__ == "__main__":
    main()