import discord
import user
from discord import app_commands
from discord.ext import commands
import json
# Charger la base de données JSON
def loaddb() -> list[user.user]:
    db = open("./db.json", "r")
    jons = json.load(db)
    db.close()
    data= jons['user']
    Users:list[user.user] = []
    for da in data:
        Users.append(user.user(da['id'],da['name'],da['amt'],da['path']))
    print(Users)
    db.close()
    return Users;

def writedb(Users:list[user.user]):
    db=open("db.json","w");
    str = """{
            "user":["""
    cpt = 0
    for user in Users:
        str+=user.tojson();
        if (cpt==len(Users)-1):
            continue;
        str+=""",
        """
    str+="""]
    }"""
    print(str)
    db.write(str);
    db.close()
Users:list[user.user]
inadduser=[]

guild_id = "1127656583346782228"  # todo :  remplacer par l'id du serveur de fusion (quand phase de test finis)

# Créer un bot avec des intents complets
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents)

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
        if not member.bot:
            await member.create_dm()
            f = discord.File("RAW.jpg",filename="RAW.jpg")
            await member.dm_channel.send(content="merci de bien vouloir renvoyer ce fichier signer",file=f)
            
        else:
            await interaction.response.send_message("Vous ne pouvez pas ajouter un bot.", ephemeral=True)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'exécuter cette commande.", ephemeral=True)


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
