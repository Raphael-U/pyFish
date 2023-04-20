from discord.ext import commands
class InteractionCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if not interaction.is_command():
            return

        command = self.bot.get_command(interaction.command_name)

        if not command:
            return

        try:
            await command(interaction)
        except Exception as error:
            print(f"An error occurred while executing the command: {error}")
            await interaction.response.send_message("An error occurred while executing the command!", ephemeral=True)


def setup(bot):
    bot.add_cog(InteractionCreate(bot))
