from discord.ui import View, Select, select
from discord import SelectOption, Interaction


class TierlistViews(View):
   def __init__(self):
      super().__init__(timeout=None)

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


  # @select(placeholder='Choose which book you want',options=self.sel_options)
   # async def selection_menu(self,interaction: Interaction,selection:Select):
   #    selected_value = selection.values[0]
   #    await interaction.response.edit_message(content=f'{selected_value} was selected!', view=None)
   #    self.stop()
   #    return selected_value
