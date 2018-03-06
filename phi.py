import discord
import asyncio
import config
import db

#Discord client PhiBot
class PhiBot(discord.Client):

	def __init__(self, lock):
		super().__init__()
		self.lock = lock 

	#When the bot is ready
	async def on_ready(self):
		print('logged in as')
		print(self.user.name)
		print(self.user.id)
		print('-----')

		await self.change_presence(game=discord.Game(name='culturology'))
	
	#Helper functions for processing commands
	async def thats_me(self, message):
		await self.send_message(message.channel, 'Hey, that\'s me!')


	async def get_funds(self, message):
		with await self.lock:
			self.send_message(message.channel, db.get_funds(message.author.name))

	#Process a users bank account
	async def process_bank_account(self, command_input, message):
	
		if len(command_input) == 1:
				print(command_input)
				await self.send_message(message.channel, 'This is where your bank info will be!')
		else:
			if command_input[1] == 'start':

				with await self.lock:
					user_not_in_bank = db.create_new_bank_account(message.author.id)

					if user_not_in_bank:
						await self.send_message(message.channel, 'Your bank account has been created and started with 200 credits!')
					else:
						await self.send_message(message.channel, 'You already have an account within our bank!')
			elif command_input[1] == 'funds':
				funds = 0
				with await self.lock:
					funds = db.get_funds(message.author.id)

				if funds == -1:
					message_to_send = '@{}, '.format(message.author.id)
					await self.send_message(message.channel, 'You need to have a bank account to have funds!')
				else:
					await self.send_message(message.channel, funds)
			elif command_input[1] == 'transfer':
				if len(command_input) < 4:
					message_to_send = '@{}, '.format(message.author.id)
					await self.send_message(message.channel, '```Sorry, this is an invalid use transfer, please try $help bank for more information```')


	#Commmand processor
	async def process_command(self, message):
		if message.content.startswith('$phi'):
			await self.thats_me(message)
		elif message.content.startswith('$cultured'):
			await self.send_message(message.channel, 'Ah, yes, our lord and savior, @cenz#4867')
		elif message.content.startswith('$goodboy'):
			await self.send_message(message.channel, 'Woof!')
		elif message.content.startswith('$bank'):
			command_input = message.content.split()
			await self.process_bank_account(command_input, message)
		elif message.content.startswith('$yt'):
			await self.send_message(message.channel, '?play https://www.youtube.com/watch?v=4yym5Og_Oeg')
		else:
			return False

		return True

	#Discord Event handlers
	async def on_message(self, message):
		valid_command = await self.process_command(message)

		#Log command to database
		if valid_command:
			user_input = message.content.split()
			with await self.lock:
				db.add_command_to_history(user_input[0], user_input[1:], message.author.name)


def shutdown():
	print('Shutting down...')
	db.close_database()

def main(loop):
	#Shared lock for keeping database information safe
	lock = asyncio.Lock()

	phi = PhiBot(lock)

	#Start and login to the bot
	try:
		loop.run_until_complete(phi.start(config.DISCORD_TOKEN))
	except KeyboardInterrupt:
		loop.run_until_complete(phi.logout())
	finally:
		loop.close()


if __name__ == '__main__':
	#Create database connection and then start all asynchronous actions
	db.create_db_connection()
	event_loop = asyncio.get_event_loop()
	main(event_loop)
