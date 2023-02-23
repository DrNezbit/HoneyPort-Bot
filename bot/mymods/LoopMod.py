import discord,datetime,asyncio,os
from discord.ext import commands,tasks


##################################################
class MyTasks():
##################################################
	def __init__(self, bot):
		self.bot = bot
		self.Loops=Loops(self.bot)
##################################################
	async def start_tasks(self):
		self.bot.MyTasks.reminder_loop.start()
##################################################
	@tasks.loop(seconds=1)
	async def reminder_loop(self):
		sent=await self.Loops.log_loop()
		if sent==True: self.bot.MyTasks.reminder_loop.change_interval(seconds=300)
		elif self.bot.MyTasks.reminder_loop.seconds==300:
			self.bot.MyTasks.reminder_loop.change_interval(seconds=1)
##################################################
##################################################	
		
##################################################
class Loops:
##################################################
	def __init__(self,client):
		self.client=client
		self.MyLogs=MyLogs(client)
##################################################
	async def log_loop(self):
		sent=await self.MyLogs.check_logs()
		return sent
##################################################
##################################################

##################################################
class MyLogs:
##################################################
	def __init__(self,bot):
		self.bot=bot
		self.logs=self.bot.Get.logs()
		self.logs.reverse()
	async def check_logs(self):
		new_logs=self.bot.Get.logs()
		new_logs.reverse()
		sent=False
		if new_logs[0] != self.logs[0]:
			self.logs=new_logs
			sent=await self.send_dm()
		return sent
##################################################
	async def send_dm(self,reset=False):
		owner_id=self.bot.owner_id
		user=await self.bot.fetch_user(int(os.environ["OWNER"]))
		user_chan=user.dm_channel
		if user_chan is None: user_chan=await user.create_dm()
		view=self.bot.MyCord.Page_View(self.bot)
		title="Alert!"
		if reset==True: title+="\nLogs Reset"
		embed=await view.get_embed(title,color="red")
		await user_chan.send(embed=embed,view=view)
		return True
##################################################
##################################################
