
while True:
    try:
        age = int(input("Please enter your age: "))
    except ValueError:
        print("Sorry I didn't understand that .")
        # better try again
        continue
    else:
        break

if age >= 18:
    print("you are able to vote in the United States!")
else:
    print("You are not able to vote in the United States .")