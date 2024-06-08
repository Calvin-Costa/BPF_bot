import discord
from db.data_handler import DataHandler

class TierlistViews(discord.ui.View):
   def __init__(self,user: discord.Member = None):
      super().__init__(timeout=None)
      #self.message: str = "No tierlist found."
      self.db = DataHandler()
      self.user = user

   @discord.ui.button(label='Show Tierlist as text', custom_id='botao_ola', style=discord.ButtonStyle.green)
   async def show_more_tierlists(self, interaction: discord.Interaction, button: discord.ui.Button):
      message = ""
      user_id = str(interaction.user.id)
      user_name = interaction.user.name
      if self.user:
          user_id = str(self.user.id)
          user_name = self.user.name
      tierlists = await self.db.load_tierlist()
      user_data = tierlists[str(interaction.guild_id)][user_id]

      for rank,novel_list in user_data.items():
         message += f"{rank}: "
         for index,novel_name in enumerate(novel_list):
               message += f"{novel_name}"
               if index < len(novel_list)-1:
                  message +=", "
         message += "\n"
      await interaction.response.send_message(f"Ok {interaction.user.name}, here's {user_name} full tierlist: \n\n{message}")
