import discord
from discord.ext import commands
import json
db = open("./db.json","r")
jons = json.load(db)
print (type(jons))
print (jons)
bot = commands.Bot('>',intents=discord.Intents.all(),help_command=None)

    
@bot.command()
async def dette(ctx, *args):
    if (len(args)==1):
        amt = args[0];
        try:
            amt =float(amt) 
            amt = int(amt*100);
            await ctx.send("ta dette est de maintenant de "+str(float(amt)/100))
        except Exception as e:
            print (e);
    if (len(args)==2):
        if "méchant d'anime" in [role.name for role in ctx.author.roles]:
            amt = args[1];
            who = args[0];
            try:
                amt =float(amt) 
                amt = int(amt*100);
                if (('<@' == who[:2])and('>'==who[-1:])):
                    user_id  = int(who.replace("<@",'').replace(">",''))
                    member = ctx.guild.get_member(user_id)
                    if member:
                        await ctx.send(f"la dette de {member.name} est maintenant de "+str(float(amt)/100))
                    else:
                        await ctx.send(f"Aucun membre trouvé avec l'ID {user_id}.")
            except Exception as e:
                print (e);
    await ctx.send(1)

ftoken = open("token.pvt","r")
token =ftoken.read()
ftoken.close()
bot.run(token=token)