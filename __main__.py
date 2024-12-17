import discord
import User
from discord import app_commands
from discord.ext import commands
import requests
import os
from dbi import *
Users:list[User.user]
inadduser=[]

guild_id = "1318570459016724570"  # todo :  remplacer par l'id du serveur de fusion (quand phase de test finis)

# Créer un bot avec des intents complets
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents)


async def get_role_by_name(bot: commands.Bot, guild_id: int, role_name: str) -> discord.Role | None:
    """
    Récupère l'objet Role à partir de son nom dans une guild en utilisant l'ID.

    Parameters:
    - bot (commands.Bot): L'instance du bot pour récupérer la guild.
    - guild_id (int): L'ID de la guild.
    - role_name (str): Le nom du rôle recherché.

    Returns:
    - discord.Role | None: L'objet Role s'il est trouvé, sinon None.
    """
    guild = bot.get_guild(guild_id)  # Récupère l'objet Guild à partir de l'ID
    if guild is None:
        return None  # La guild n'a pas été trouvée

    for role in guild.roles:
        if role.name == role_name:
            return role
    return None

def has_role(user, role_name):
    return role_name in [role.name for role in user.roles]

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f"Commandes slash synchronisées: {len(synced)}")
    except Exception as e:
        print(f"Erreur de synchronisation: {e}")
    try: 
        Users=loaddb()
    except Exception as e:
        print(f"Erreur de chargement de la db: {e}")

@bot.tree.command(name="dette", description="Gérer les dettes d'un utilisateur", guild=discord.Object(id=guild_id))
@app_commands.describe(member="Mention de l'utilisateur", amount="Montant de la dette")
async def dette(interaction: discord.Interaction, member: discord.Member = None, amount: float = None):
    if amount is None:
        amount = 0.7;
    if member is None:
        # Mise à jour de la dette pour l'auteur
        Users = loaddb()
        user  =next((user for user in Users if user.id == interaction.user.id), None)
        if (user):
            amount+=user.amt
            await interaction.response.send_message(f"Votre dette est maintenant de {amount:.2f}.")
            user.amt = amount;
            writedb(Users)
        else:
            await interaction.response.send_message("Vous n'avez pas la permission de prendre une dette", ephemeral=True)

    else:
        if has_role(interaction.user, "BG"): 
            Users = loaddb()
            user  =next((user for user in Users if user.id == member.id), None)
            if (user):
                amount+=user.amt
                # Mise à jour de la dette pour un autre utilisateur
                await interaction.response.send_message(f"La dette de {member.display_name} est maintenant de {amount:.2f}.")
            await interaction.response.send_message(f"{member.display_name} n'a pas la permission de prendre une dette", ephemeral=True)
        else:
            await interaction.response.send_message("Vous n'avez pas la permission de modifier les dettes des autres.", ephemeral=True)

@bot.tree.command(name="add", description="Ajouter un utilisateur", guild=discord.Object(id=guild_id))
@app_commands.describe(member="Membre à ajouter")
@app_commands.checks.has_permissions(administrator=True)
async def add(interaction: discord.Interaction, member: discord.Member):
    
    if has_role(interaction.user, "Président de l'assosiation fusion"):
        await interaction.response.defer()
        if not member.bot:
            await member.create_dm()
            f = discord.File("RAW.png",filename="RAW.png")
            await member.dm_channel.send(content="merci de bien vouloir renvoyer ce fichier signer",file=f)
            add = loadadddb()
            add.append(User.inadduser(member.id,member.name))
            writeadddb(add)
            await interaction.followup.send(f"merci, tres chere ~~dictateur~~ nous allons essayer d'ajouter {member.mention}")
        else:
            await interaction.followup.send("Vous ne pouvez pas ajouter un bot.", ephemeral=True)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'exécuter cette commande.", ephemeral=True)
@bot.tree.command(name="toverify",description="permet de renvoyer l'image au bot",guild=discord.Object(id=guild_id))
@app_commands.describe(file="le document")
async def toverify(interaction: discord.Interaction,file:str):
    adddb = loadadddb()
    await interaction.response.defer()
    user  =next((user for user in adddb if user.id == interaction.user.id), None)
    if (user):
        text = requests.get(file).content
        f = open(f"./unvalidate/{user.id}.png","wb")
        f.write(text);
        f.close();
        user.path= f"./unvalidate/{user.id}.png"
        fi = discord.File(f"./unvalidate/{user.id}.png")
        await interaction.followup.send(content="le président doit maintenant valider votre document",ephemeral=True)
        pres =await  get_role_by_name(bot=bot,guild_id=int(guild_id),role_name="Président de l'assosiation fusion")
        if (pres):
            await interaction.channel.send(content=f"{pres.mention} faites /validate {interaction.user.mention} pour valider ce document",file=fi)
            writeadddb(adddb);
        else: 
            await interaction.channel.send(content="something went wrong");
    else:
        await interaction.response.send_message("Vous n'etes pas sur la liste d'ajout", ephemeral=True)
    return
@bot.tree.command(name="validate", description="permet de valider le document",guild=discord.Object(id=guild_id))
@app_commands.describe(member="Membre à ajouter")
@app_commands.checks.has_permissions(administrator=True)
async def validate(interaction: discord.Interaction, member:discord.Member):
    if has_role(interaction.user, "Président de l'assosiation fusion"):
        adddb=loadadddb()
        user  =next((user for user in adddb if user.id == interaction.user.id), None)
        if(user):
            if(user.path!=""):
                newdb:list[User.inadduser]= []
                for i in range(len(adddb)):
                    d= adddb.pop()
                    if (d==user):
                        continue;
                    newdb.append(d)
                writeadddb(newdb)
                Users = loaddb()
                os.system(f"mv {user.path} ./rated/{user.id}.png")
                user.path = f"./rated/{user.id}.png"
                Users.append(User.user(user.id,user.name,0,user.path))
                writedb(Users)
                await interaction.response.send_message(f"l'utilisateur {member.mention} est maintenant ajouter a la base de donnée")
            else:
                print(user)
                await interaction.response.send_message(f"merci d'attendre le document de {member.mention} avant")
        else:
            await interaction.response.send_message("merci de faire la commande /add avant")
    else:
        await interaction.response.send_message("vous n'etes pas le président")

@bot.tree.command(name="checkev", description="affiche la dette de tout le monde", guild=discord.Object(id=guild_id))
@app_commands.checks.has_permissions(administrator=True)
async def check_ev(interaction: discord.Interaction):
    Users = loaddb()
    content=''
    for user in Users:
        content+= str(user)+"\n"
    emb = discord.Embed(description=content)
    await interaction.response.send_message(embed=emb)

@bot.tree.command(name="rib", description="envoie le rib de fusion", guild=discord.Object(id=guild_id))
async def rib(interaction: discord.Interaction):
    emb = discord.Embed(title="le RIB de fusion",description="IBAN : FR76 1790 6000 9020 6106 4500 097\nBIC : AGRIFRPP879")
    await  interaction.response.send_message(content="tu as le rib maintenant paye",embed=emb)

# Lancer le bot
ftoken = open("token.pvt", "r")
token = ftoken.read()
ftoken.close()

bot.run(token=token)
