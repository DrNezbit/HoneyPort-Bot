import discord
import time,datetime
		
		
##################################################
##################################################
Interaction=discord.Interaction
Button=discord.Button
##################################################
class Message:
##################################################
	def __init__(self): self.self=self
##################################################
	async def send(self,interaction,embed,view=None,hide=False):
		if view is None:
			await interaction.response.send_message(embed=embed,ephemeral=hide)
		else:
			await interaction.response.send_message(embed=embed,view=view,ephemeral=hide)
##################################################		
	async def swap(self,interaction,embed,view=None):
		if view is None:
			await interaction.edit_original_response(embed=embed)
		else:
			await interaction.edit_original_response(embed=embed,view=view)
##################################################
##################################################

##################################################
class Embed:
##################################################
	def __init__(self): self.self=self
##################################################
	async def create(self,title,desc,color=None,thumb=None,image=None,footer=None):
		new_color=await self.get_color(color)
		if new_color is None: new_color=discord.Color.random()
		embed=discord.Embed(title=title,description=desc,color=new_color)
		embed.set_footer(text=footer)
		if thumb !=None: embed.set_thumbnail(url=thumb)
		if image !=None: embed.set_image(url=image)
		return embed
##################################################
	async def get_color(self,color):
		try: color=color.lower()
		except: return color
		if color=="blue": color=discord.Color.blue()
		elif color=="red": color=discord.Color.brand_red()
		elif color=="green": color=discord.Color.brand_green()
		elif color=="grey": color=discord.Color.dark_gray()
		elif color=="purple": color=discord.Color.purple()
		elif color=="teal": color=discord.Color.teal()
		elif color=="yellow": color=discord.Color.yellow()
		elif color=="orange": color=discord.Color.orange()
		elif color=="random": color=None
		return color
##################################################
##################################################

##################################################
class Get:
##################################################
	def __init__(self): self.self=self
##################################################
	async def object(self,obj_id): 
		obj=discord.Object(id=obj_id) ; return obj
##################################################
	def logs(self):
		with open("./logs/HoneyPort.log","r") as f:
			data=f.readlines()
		return data
##################################################
##################################################


##################################################
class Time:
##################################################
	def __init__(self): self=self
##################################################
	async def now(self,timestamp=False):
		now= datetime.datetime.utcnow()
		if timestamp==True: 
			now=now.replace(tzinfo=datetime.timezone.utc)
		return now
##################################################
	async def local_timestamp(self,date_time,ret_format="f"):
		try: date_time=await self.from_int(date_time)
		except: pass
		"""
Style	Example Output	Description

t		 	22:57					Short Time
T			22:57:58		 	  Long Time
d			17/05/2016		Short Date
D			17 May 2016	   Long Date
f 	17 May 2016 22:57	Short Date Time	(default)
F	Tuesday, 17 May 2016 22:57	Long Date Time
R			5 years ago	Relative Time
		"""
		formats=["t","T","d","D","f","F","R"]
		if ret_format not in formats: return "bad format"
		local=discord.utils.format_dt(date_time,style=ret_format)
		return local
##################################################
	async def to_int(self,date_time):
		unix_ts=time.mktime(date_time.timetuple())
		return int(unix_ts)
##################################################
	async def from_int(self,int_time):
		date_time=time.ctime(int(int_time)) #Sun Jun 20 23:21:05 1993
		if "  " in date_time: date_time=date_time.replace("  "," 0")
		ret_date=datetime.datetime.strptime(date_time,"%a %b %d %H:%M:%S %Y")
		ret_date=ret_date.replace(tzinfo=datetime.timezone.utc)
		return ret_date
##################################################
	async def calculate(self,created_at,m=0,h=0,d=0):
		end_t=created_at + datetime.timedelta(minutes=m,hours=h,days=d)
		return end_t
##################################################


##################################################
##################################################
class Page_View(discord.ui.View):
##################################################
	def __init__(self,client):
		super().__init__(); self.timeout=None
		self.client=client
		self.desc_list=client.Get.logs()
		self.desc_list.reverse()
		self.page=1
		self.limit=5
		self.end=len(self.desc_list)/self.limit
		if not self.end.is_integer(): self.end=int(self.end)+1
		if self.end<1: self.end=1
		self.title=None ; self.footer="" ; self.thumb=None
		self.msg=client.msg ; self.emb=client.emb
		self.start_index=0 ; self.end_index=self.limit
		self.back_button.disabled=True
		self.embed=None ; self.note=""
		if len(self.desc_list) <= self.limit:
			self.desc="\n".join(self.desc_list)
			self.back_button.disabled=True
			self.next_button.disabled=True
		else: 
			self.desc="\n".join(self.desc_list[self.start_index : self.end_index])
##################################################		
	async def interaction_check(self,interaction: discord.Interaction):
		msg=await interaction.message.fetch()
		author=interaction.user
		if msg is not None: 
			inter=msg.interaction
			if inter is not None: author=inter.user
		if author.id!=interaction.user.id:
			await interaction.response.send_message("You cannot use this button",ephemeral=True)
		return author.id==interaction.user.id
##################################################
	async def refresh(self):
		old_end=self.end
		self.desc_list=self.client.Get.logs()
		self.desc_list.reverse()
		self.end=len(self.desc_list)/self.limit
		if not self.end.is_integer(): self.end=int(self.end)+1
		if self.end<1: self.end=1
		if old_end!=self.end: self.start_index=0 ; self.end_index=self.limit
		try: to_join=self.desc_list[self.start_index:self.end_index]
		except: to_join=self.desc_list[self.start_index:]
		self.desc="\n".join(to_join)
##################################################
	async def get_embed(self,title,note="",footer="",thumb=None,color=None,image=None):
		if self.desc=="":
			self.page=1 ; self.start_index=0 ; self.end_index=self.limit
			await self.refresh()
			self.back_button.disabled=True
		if self.page==1: self.back_button.disabled=True
		if self.end==1: self.next_button.disabled=True
		self.title=title
		self.note=note
		self.footer=footer
		self.thumb=thumb
		if self.note !="":desc=f"{self.note} \n \n{self.desc}"
		else: desc=self.desc
		if not len(self.desc_list)<=self.limit:
			footer=f"{self.footer} \nPage {self.page} / {int(self.end)}"
		embed=await self.emb.create(self.title,desc,thumb=self.thumb,footer=footer,color=color,image=image)
		return embed
##################################################
	async def update_embed(self,interaction):
		await self.refresh()
		self.embed=await self.get_embed(self.title,self.note,self.footer,self.thumb)
		await interaction.response.edit_message(embed=self.embed,view=self)
##################################################
	@discord.ui.button(row=0,style=discord.ButtonStyle.primary,label="back",custom_id="logs_back")
	async def back_button(self, interaction: Interaction, button):
		self.start_index=self.start_index-self.limit
		self.end_index=self.end_index-self.limit
		self.page-=1
		if self.start_index==0: self.back_button.disabled=True
		else: self.back_button.disabled=False
		self.next_button.disabled=False
		await self.update_embed(interaction)
##################################################
	@discord.ui.button(row=0,style=discord.ButtonStyle.gray,label="🔁",custom_id="logs_refresh")
	async def refresh_button(self, interaction: Interaction, button):
		self.page=1 ; self.start_index=0 ; self.end_index=self.limit
		await self.refresh()
		self.back_button.disabled=True
		if len(self.desc_list) <= self.limit: self.next_button.disabled=True
		else: self.next_button.disabled=False
		await self.update_embed(interaction)
##################################################
	@discord.ui.button(row=0,style=discord.ButtonStyle.primary,label="next",custom_id="logs_next")
	async def next_button(self, interaction: Interaction, button):
		self.start_index=self.start_index+self.limit
		self.end_index=self.end_index+self.limit
		self.page+=1
		if self.end_index-1>=len(self.desc_list)-1: 
			self.next_button.disabled=True
		else: self.next_button.disabled=False
		self.back_button.disabled=False
		await self.update_embed(interaction)
##################################################
##################################################
