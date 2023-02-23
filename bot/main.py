import discord,os,datetime,asyncio
from discord.ext import commands,tasks
from mymods import MyCord,LoopMod

##################################################
port=22
os.popen(f"python HoneyPort.py -p {port}") ; print(f"Listener Started on {port}")
while "HoneyPort.log" not in os.listdir("./logs"):
	asyncio.run(asyncio.sleep(1))
##################################################
##################################################
intents = discord.Intents.default()
class MyClient(commands.Bot):
	def __init__(self):
		#print("#########################################")
		super().__init__(command_prefix="-",intents=intents)
		self.guild_id=os.environ["GUILD"]
		self.MyCord=MyCord
		self.emb=MyCord.Embed()
		self.msg=MyCord.Message()
		self.Get=MyCord.Get()
		self.MyTasks=LoopMod.MyTasks(self)
##################################################
	async def setup_hook(self):
		for ext in self.cog_list(): await self.load_extension(ext)
		# This copies the global commands over to your guild.
		MY_GUILD = await self.Get.object(self.guild_id)
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)
		await self.start_persistence()
		print("##########################################")
##################################################
	async def start_persistence(self):
		self.add_view(self.MyCord.Page_View(self))
##################################################
	def cog_list(self):
		mycogs=[]
		for f in os.listdir("./cogs"):
			if f.endswith(".py"): mycogs.append(f"cogs.{f[:-3]}")
		return mycogs
##################################################
	
##################################################
client = MyClient() ; tree = client.tree
##################################################
#	ON READY
@client.event
async def on_ready():
	await client.MyTasks.start_tasks()
	print(f'Logged in as {client.user} On {len(client.guilds)} servers')
	print("##########################################")
##################################################

##################################################
#	ERRORS
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
	print(error)
	title="Error Encountered"
	desc=error
	embed=await client.emb.create(title,desc,color="red")
	await client.msg.send(interaction,embed,hide=True)
##################################################

##################################################


##################################################
client.run(os.environ["TOKEN"])
##################################################