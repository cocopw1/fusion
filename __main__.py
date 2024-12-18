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

async def get_channel_by_id(bot: discord.Client, channel_id: int):
    """
    Retourne l'objet TextChannel correspondant à un ID donné.
    
    :param bot: Instance du bot ou client Discord.
    :param channel_id: ID du channel à récupérer.
    :return: Objet TextChannel si trouvé, sinon None.
    """
    channel = bot.get_channel(channel_id)  # Recherche dans le cache
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)  # Récupération directe via l'API Discord
        except discord.NotFound:
            print(f"Le channel avec l'ID {channel_id} n'existe pas.")
        except discord.Forbidden:
            print(f"Accès refusé au channel avec l'ID {channel_id}.")
        except discord.HTTPException as e:
            print(f"Erreur HTTP lors de la tentative de récupération du channel : {e}")
    return channel
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

@bot.event
async def on_message(message:discord.Message):
    print("test")
    # Vérifiez si le message contient une pièce jointe
    if message.attachments:
        for attachment in message.attachments:
            # Vérifiez si le fichier est un PDF
            if (attachment.filename.endswith(".pdf") or attachment.filename.endswith(".docx")):
                adddb = loadadddb()
                user  =next((user for user in adddb if user.id == message.author.id), None)
                if (user):
                    if (attachment.filename.endswith(".pdf")):
                        user.path= f"./unvalidate/{user.id}.pdf"
                    if (attachment.filename.endswith(".docx")):
                        user.path= f"./unvalidate/{user.id}.docx"
                    await attachment.save(user.path)
                    
                    print(f"Fichier enregistré sous : {user.path}")
                    fi = discord.File(user.path)
                    await message.channel.send(content="le président doit maintenant valider votre document")
                    pres =await  get_role_by_name(bot=bot,guild_id=int(guild_id),role_name="Président de l'assosiation fusion")
                    confchan =await  get_channel_by_id(bot=bot,channel_id=1318579901816897586)
                    if ((pres)and(confchan)):
                        await confchan.send(content=f"{pres.mention} faites /validate {message.author.mention} pour valider ce document",file=fi)
                        writeadddb(adddb);
                    else: 
                        await message.channel.send(content="something went wrong");
@bot.tree.command(name="help",description="affiche l'aide", guild=discord.Object(id=guild_id))
async def help(interaction:discord.Interaction):
    str ="""```
pour le 
/add
/toverify
/validate

/add nécesite le role pres : permet de lancer la procedure d'ajout de la personne en argument member

ensuite 
/toverify
permet de faire verifier le fichier png au pres passer sous forme d'url (envoyer dans le channel puis copier lien)en argument
/validate nessecite le role pres
permet de valider le fichier d'ajout envoyer par @member en argument
```
```
pour le /dette
si role @BG
  peut modifier la dette d'autrui si il est ajouter au préalable
sinon 
  permet de modifier sa propre dette si ajouter au préalable

default value
amount = 0.7
member = self
```
```
pour le 

/help affiche l'aide
                                      
/rib rien cela envoie juste le rib

/check_ev
permet au admin (extend sur le serveur de vrai fusion BG) de check la dette de tout le monde
```"""
    await interaction.response.send_message(str)

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
        adddb = loadadddb()
        await interaction.response.defer()
        aduser  =next((user for user in adddb if user.id == interaction.user.id), None)
        db = loadadddb()
        user  =next((user for user in db if user.id == interaction.user.id), None)
        if ((not member.bot)and (not user)and (not aduser)):
            await member.create_dm()
            f = discord.File("RAW.docx",filename="RAW.docx")
            await member.dm_channel.send(content="merci de bien vouloir renvoyer ce fichier signer",file=f)
            add = loadadddb()
            add.append(User.inadduser(member.id,member.name))
            writeadddb(add)
            await interaction.followup.send(f"merci, tres chere ~~dictateur~~ nous allons essayer d'ajouter {member.mention}")
        else:
            await interaction.followup.send("Vous ne pouvez pas ajouter un bot.", ephemeral=True)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'exécuter cette commande.", ephemeral=True)
# @bot.tree.command(name="toverify",description="permet de renvoyer l'image au bot",guild=discord.Object(id=guild_id))
# @app_commands.describe(file="le document")
# async def toverify(interaction: discord.Interaction,file:str):
    # adddb = loadadddb()
    # await interaction.response.defer()
    # user  =next((user for user in adddb if user.id == interaction.user.id), None)
    # if (user):
    #     text = requests.get(file).content
    #     f = open(f"./unvalidate/{user.id}.pdf","wb")
    #     f.write(text);
    #     f.close();
    #     user.path= f"./unvalidate/{user.id}.pdf"
    #     fi = discord.File(f"./unvalidate/{user.id}.pdf")
    #     await interaction.followup.send(content="le président doit maintenant valider votre document",ephemeral=True)
    #     pres =await  get_role_by_name(bot=bot,guild_id=int(guild_id),role_name="Président de l'assosiation fusion")
    #     if (pres):
    #         await interaction.channel.send(content=f"{pres.mention} faites /validate {interaction.user.mention} pour valider ce document",file=fi)
    #         writeadddb(adddb);
    #     else: 
    #         await interaction.channel.send(content="something went wrong");
    # else:
    #     await interaction.response.send_message("Vous n'etes pas sur la liste d'ajout", ephemeral=True)
    # return
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
                if user.path.endswith(".pdf"):
                    os.system(f"mv {user.path} ./rated/{user.id}.pdf")
                    user.path = f"./rated/{user.id}.pdf"
                if user.path.endswith(".docx"):
                    os.system(f"mv {user.path} ./rated/{user.id}.docx")
                    user.path = f"./rated/{user.id}.docx"
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
