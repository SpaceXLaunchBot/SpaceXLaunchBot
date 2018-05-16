from discord import Embed

from colours import hexColours

nextLaunchErrorEmbed = Embed(title="Error", description="An launchInfoEmbed error occurred, contact <@263412940869206027>", color=hexColours["errorRed"])
apiErrorEmbed = Embed(title="Error", description="An API error occurred, contact <@263412940869206027>", color=hexColours["errorRed"])
generalErrorEmbed = Embed(title="Error", description="An error occurred, contact <@263412940869206027>", color=hexColours["errorRed"])

def fatalError(message):
    print("\nERROR:\n" + message)
    sys.exit(-1)
