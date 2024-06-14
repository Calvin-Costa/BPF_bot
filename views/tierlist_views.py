import discord
from db.data_handler import DataHandler

class TierlistViews(discord.ui.View):
   def __init__(self,guild_id: int, user_id,user_name:str, user: discord.Member = None):
      super().__init__(timeout=None)
      #self.message: str = "No tierlist found."
      self.db = DataHandler()
      self.user = user
      self.guild_id = guild_id
      self.user_id = user_id
      self.user_name = user_name
      self.db = DataHandler()

   @discord.ui.button(label='Show Tierlist as text', custom_id='botao_ola', style=discord.ButtonStyle.green)
   async def show_more_tierlists(self, interaction: discord.Interaction, button: discord.ui.Button):
      #message = ""
      user_id = self.user_id
      user_name = self.user_name
      # se a tierlist for de outra pessoa:
      if self.user:
          user_id = await self.db.get_or_create_user_model(self.user.id, self.guild_id)
          user_name = self.user.display_name
      user_data = await self.db.show_tierlist_entries(user_id, self.guild_id)
      message_list = ['']
      for rank,novel_list in user_data.items():
         #message = f"  ** {rank}** \n"  
         message = ''
         if len(novel_list) == 0:
            message += 'Empty. '

         for index,novel_name in enumerate(novel_list):
            message += f"⌜{novel_name}⌟ "
            if index < len(novel_list)-1:
               message +=" "
         if message_list[0] == '':
            message_list[0] = message
         else:
            message_list.append(message)
         #message += "\n"
         #message += ''
      embed_rank_s = discord.Embed(color=discord.Color.brand_red(), description=message_list[0], title='  ** Rank S ** ')
      embed_rank_a = discord.Embed(color=discord.Color.dark_orange(), description=message_list[1], title=" ** Rank A **")
      embed_rank_b = discord.Embed(color=discord.Color.orange(), description=message_list[2], title=" ** Rank B** ")
      embed_rank_c = discord.Embed(color=discord.Color.yellow(), description=message_list[3], title=" ** Rank C **")
      embed_rank_d = discord.Embed(color=discord.Color.green(), description=message_list[4], title=" ** Rank D **")

      await interaction.response.send_message(f"Ok {interaction.user.display_name}, here's {user_name}'s full tierlist:", embeds=[embed_rank_s,embed_rank_a,embed_rank_b,embed_rank_c,embed_rank_d])
