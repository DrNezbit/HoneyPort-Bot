import discord,os
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from typing import Optional,Literal


Button=discord.Button
Interaction=discord.Interaction
##################################################
def bot_owner(interaction):
	return int(interaction.user.id)==int(os.environ["OWNER"])
##################################################
class CommandCog(commands.Cog):
##################################################
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.emb=self.bot.emb
		self.msg=self.bot.msg
##################################################
	
##################################################
#RESTART COMMAND
##################################################
	@app_commands.command(name="restart-pot",description="Owner only. Restarts the bot")
	@app_commands.check(bot_owner)
	async def restart(self,interaction):
		embed=await self.bot.emb.create("Restarting","Closing bot connection",color="orange")
		await self.bot.msg.send(interaction,embed,hide=True)
		print("----BOT RESTARTED----")
		print("########## Connection Closed ############")
		await self.bot.close()
##################################################
#LOGS
##################################################
	@app_commands.command(name="logs",description="view logs")
	@app_commands.check(bot_owner)
	async def view_logs(self,interaction):
		view=self.bot.MyCord.Page_View(self.bot)
		embed=await view.get_embed("Logs",color="green")
		await self.msg.send(interaction,embed=embed,view=view)
##################################################
#CLEAR LOGS
##################################################
	@app_commands.command(name="clear-logs",description="clear logs")
	@app_commands.check(bot_owner)
	async def clear_logs(self,interaction):
		embed=await self.emb.create("Logs Cleared","Logs have been reset to last entry",color="orange")
		logs=self.bot.Get.logs()
		last_log=logs[-1]
		with open("./logs/HoneyPort.log","w") as f:
			f.write(last_log)
		await self.msg.send(interaction,embed=embed)
		await self.bot.MyTasks.Loops.MyLogs.send_dm(reset=True)
##################################################
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(CommandCog(bot))