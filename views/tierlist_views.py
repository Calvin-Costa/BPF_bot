from math import ceil
from discord.ui import View, Select, select, button, Button
from discord import SelectOption, Interaction, Color, Embed, ButtonStyle, File


class TierlistView(View):
   current_page = 1
   separator = 10
   def __init__(self):
      super().__init__(timeout=None)
      self.ranks = {"Rank S": Color.brand_red, "Rank A": Color.dark_orange, "Rank B": Color.orange, "Rank C": Color.yellow, "Rank D": Color.green, "Rank E": Color.dark_teal}
   async def send_first_message(self, interaction:Interaction):
      embeds_list = await self.get_embeds_list(self.separator,0)
      
      self.update_buttons()
      await interaction.response.send_message(content=self.bot_message,embeds=embeds_list, view=self)

   async def create_embed(self, data, rank):
      rank_name = list(self.ranks.keys())[rank]
      embed = Embed()
      message = ''
      if not data:
         message = 'Empty.'
      if data:
         for book in data:
            message += f"「{book}」"
         #print(message)
      embed.add_field(name=rank_name,value=message)
      embed.color=self.ranks[rank_name]()
      return embed
   
   def update_buttons(self):
      self.current_page_button.label = f'{self.current_page}'
      self.current_page_button.disabled = True
      if self.current_page == 1:
         self.first_page_button.disabled = True
         self.previous_page_button.disabled = True
         self.next_page_button.disabled = True
         self.last_page_button.disabled = True
      if self.current_page > 1:
         self.first_page_button.disabled = False
         self.previous_page_button.disabled = False
         self.next_page_button.disabled = False
         self.last_page_button.disabled = False
      if self.current_page == (ceil(self.max_length/self.separator)):
         self.first_page_button.disabled = False
         self.previous_page_button.disabled = False
         self.last_page_button.disabled = True
         self.next_page_button.disabled = True

   @button(label='|<<', style=ButtonStyle.green)
   async def first_page_button(self, interaction:Interaction, button:Button):
      if self.current_page > 1:
         self.current_page = 1
         self.update_buttons()
      until_book = self.current_page * self.separator
      from_book = until_book - self.separator
      await self.update_message(interaction, until_book, from_book)

   @button(label='<', style=ButtonStyle.blurple)
   async def previous_page_button(self, interaction:Interaction, button:Button):
      if self.current_page > 1:
         self.current_page += -1
         self.update_buttons()
      until_book = self.current_page * self.separator
      from_book = until_book - self.separator
      await self.update_message(interaction, until_book, from_book)

   @button(style=ButtonStyle.gray, disabled=True)
   async def current_page_button(self, interaction:Interaction, button:Button):
      ...

   @button(label='>', style=ButtonStyle.blurple)
   async def next_page_button(self, interaction:Interaction, button:Button):
      if self.current_page < (ceil(self.max_length/self.separator)):
         self.current_page += 1
         self.update_buttons()
      until_book = self.current_page * self.separator
      from_book = until_book - self.separator
      
      await self.update_message(interaction, until_book, from_book)

   @button(label='>>|', style=ButtonStyle.green)
   async def last_page_button(self, interaction:Interaction, button:Button):
      if self.current_page < (ceil(self.max_length/self.separator)):
         self.current_page = ceil(self.max_length/self.separator)
         self.update_buttons()
      until_book = self.current_page * self.separator
      from_book = until_book - self.separator
      await self.update_message(interaction,self.max_length, from_book)

   async def update_message(self, interaction, until_book, from_book):
      embed_list = await self.get_embeds_list(until_book, from_book)
      await interaction.response.edit_message(content=self.bot_message, embeds=embed_list,view = self)

   async def get_embeds_list(self, until_book, from_book):
       embed_list = []
       for rank_number,listting in enumerate(self.data):
         if len(listting[from_book:until_book]) == 0:
            data_to_send = ''
         else:
            data_to_send = listting[from_book:until_book]   
         embed_list.append(await self.create_embed(data_to_send,rank_number))
       #embed_list.append(Embed(title=f"Page: {self.current_page}"))
       return embed_list



class SelectMenuView(View):
   def __init__(self, sel_options):
      super().__init__()
      self.sel_options = sel_options
      self.sel_value = None
      self.add_item(self.SelectMenu(sel_options))

   class SelectMenu(Select):
         def __init__(self, sel_options):
            super().__init__(placeholder='Choose which book you meant', options=sel_options)
         async def callback(self, interaction: Interaction):
            self.view.sel_value = self.values[0]
            await interaction.response.edit_message(content=f"{self.values[0]} was selected!", view=None)
            self.view.stop()
