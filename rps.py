import redis
import random
import getpass

def rock_paper_scissors():
	#Create a Redis object and connect to our Redis server
	r = redis.Redis('localhost')

	#Authenticate user
	response = raw_input("Welcome to Rock Paper Scissors! Are you a new user? (y/n)  ")
	welcome_prompt = response.upper()	
	valid = False
	
	if(welcome_prompt == "Y"):
		#Add new user when valid username entered
		while(not valid):
			username = raw_input("Choose a username: ")
			new_password = getpass.getpass(prompt="Choose a password: ") #hide user input
			#Check if username exists
			if(r.hexists(username, "password")):
				print("Username already taken.")
			else:
				valid = True
				#Add hash
				r.hmset(username, {"password": new_password, "games_played": 0})
				#Add user to Sorted Set
				r.zadd("player_scores", username, 0)
	elif(welcome_prompt == "N"):
		start_validation = True
		
		while(start_validation):
			valid_name = False
			#Validate username
			while(not valid_name):
				username = raw_input("Enter username: ")
				if(not r.hexists(username, "password")):
					print("Invalid username.")
				else:
					valid_name = True

			#Validate password
			password_attempt = getpass.getpass(prompt="Enter your password: ")
			if(password_attempt == r.hget(username, "password")):
				start_validation = False
			else:
				print("Invalid password.")
	else:
		print("Sorry, not a valid response. Bye!")
		exit()
	
	options = ["ROCK", "PAPER", "SCISSORS"]
	new_game = True

	while(new_game):
		print("Let's play! Each game has a maximum of 3 non-tied rounds. Players receive 5 points for each tie, 10 points for each round won and 30 bonus points for every game won. \n")
		current_round = 1
		user_wins = 0
		user_score = 0	
	
		#3 non-tying rounds to a game
		while(current_round <= 3):
			comp_choice = random.choice([0, 1, 2])
			user_choice = int(raw_input("Enter 0 for ROCK, 1 for PAPER, or 2 for SCISSORS: "))

			print("I threw: " + options[comp_choice])
			print("You threw: " + options[user_choice])

			#Compare throws
			if(user_choice == comp_choice):
				print("Tie! \n")
				user_score += 5
			elif((user_choice - comp_choice) % 3 == 1):
				print("You win round " + str(current_round) + "! \n")
				user_score += 10 
				user_wins += 1
				current_round += 1
			else:
				print("You lose round " + str(current_round) + "! \n")
				current_round += 1

			#No third round if user or comp has 2 wins
			if(current_round == 3 and user_wins != 1):
				break

		#Declare game winner
		if(user_wins == 2):
			print("You win the game! \n")
			user_score += 30
		else:
			print("I win the game, puny human! \n")

		#Add score to player's cumulative score			
		r.zincrby("player_scores", username, user_score)

		#Display all player scores in descending order
		scoreboard = r.zrevrange("player_scores", 0, -1, withscores=True)
		print("Check your rank on the Scoreboard!")
		for i, j in scoreboard:
			print i + ": " + str(j) + '\n'
	
		answer = raw_input("Play again? (y/n) ")
		if(answer.upper() == "N"):
			#end game
			print("Goodbye!")
			new_game = False
	
#Call function
rock_paper_scissors()
