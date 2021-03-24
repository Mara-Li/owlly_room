import discord
from discord.colour import Color
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
from discord.ext.commands import TextChannelConverter as tcc
import sqlite3
import re
from discord import Colour
import os.path
import json
import asyncio
import unidecode
import glob

class Personnage():
	def __init__(self):
		self.nom = "nom"
		self.prenom = "prenom"
		self.surnom = "surnom"
		self.age = "age"
		self.anniversaire = "birthday"
		self.sexe = "sexe"
		self.race = "race"
		self.metier = "metier"
		self.yeux = "yeux"
		self.cheveux = "cheveux"
		self.taille = "taille"
		self.poids = "poids"
		self.peau = "peau"
		self.marques = "marques"
		self.image = "link"

class presentation (commands.Cog, name="Présentation", description="Permet de débuter la présentation d'un personnage suite à la validation d'une fiche."):
	def __init__(self, bot):
		self.bot = bot
	
	async def forme (member: discord.Member, chartype):
		f = open(f"fiche/{chartype}_{member}.txt", "r", encoding="utf-8")
		data=f.readlines()
		f.close()
		msg="error"
		if (len(data) > 0):
			data = "".join(data)
			data = data.replace("\'", "\"")
			perso = json.loads(data)
			if "image" in perso.keys():
				nom = perso.get("nom")
				prenom = perso.get("prenom")
				age = perso.get("age")
				surnom=perso.get("surnom")
				anniversaire=perso.get("anniversaire")
				sexe=perso.get("sexe")
				race=perso.get("race")
				metier=perso.get("metier")
				yeux=perso.get("yeux")
				cheveux=perso.get("cheveux")
				taille=perso.get("taille")
				poids=perso.get("poids")
				peau=perso.get("peau")
				marque=perso.get("marques")
				img=perso.get("image")
				msg = f"─────༺ Présentation ༻─────\n**__Nom__** : {nom}\n**__Prénom__** : {prenom}\n**__Surnom__** : {surnom}\n**__Âge__** : {age} | {anniversaire}\n**__Sexe__** : {sexe}\n**__Race__** : {race}\n**__Métier__** : {metier}\n\n──────༺Physique༻──────\n**__Yeux__** : {yeux}\n**__Cheveux__** : {cheveux}\n**__Taille__** : {taille}\n**__Poids__** : {poids}\n**__Peau__** : {peau}\n**__Marques__** : {marque}\n\n⋆⋅⋅⋅⊱∘──────∘⊰⋅⋅⋅⋆\n*Auteur* : {member.mention}\n{img}"
		return msg

	async def start_presentation(self, ctx, member: discord.Member, chartype):
		template = vars(Personnage())
		def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		emoji=["✅", "❌"]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		if not os.path.isfile(f'fiche/{chartype}_{member}{member}.txt'):
			perso = {}
		else:
			f = open(f"fiche/{chartype}_{member}{member}.txt", "r", encoding="utf-8")
			data = f.readlines()
			f.close()
			if (len(data) > 0):
				data = "".join(data)
				data = data.replace("\'", "\"")
				perso = json.loads(data)
			else:
				perso = {}
		f = open(f"fiche/{chartype}_{member}{member}.txt", "w", encoding="utf-8")
		while "link" not in perso.keys():
			for t in template.keys():
				if t not in perso.keys():
					champ=t.capitalize()
					if champ == "Desc":
						champ = "Description physique"
					elif champ == "Image":
						champ = "Lien vers le faceclaim"
					elif champ == "Prenom":
						champ = "Prénom"
					elif champ == "Anniversaire":
						champ = "Date d'anniversaire"
					elif champ == "Metier":
						champ = "Métier"
					q=await member.send(f"{champ} ?\n Si votre perso n'en a pas, merci de mettre `/` ou `NA`.")
					rep = await self.bot.wait_for("message", timeout="300", check=checkRep)
					try:
						if rep.content.lower() == "stop":
							await member.send("Mise en pause. Vous pourrez reprendre plus tard avec la commande `fiche -reprise`")
							f.write(str(perso))
							f.close()
							return "NOTdone"
						elif rep.content.lower()=="cancel":
							await member.send("Annulation de la présentation.")
							f.close()
							os.remove(f"fiche/{chartype}_{member}.txt")
							await q.delete()
							await rep.delete()
							return "delete"
						else:
							perso.update({t: rep.content})
					except asyncio.TimeoutError:
						await member.send("Timeout ! Enregistrement des modifications.")
						f.write(str(perso))
						f.close()
						return "NOTdone"
		f.write(str(perso))
		f.close()
		msg=await self.forme(member)
		if msg != "error":
			await q.edit(content="Votre présentation est donc : \n {msg}. Validez-vous ses paramètres ?")
			await q.add_reaction("✅")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "✅":
				await q.edit(content="Fin de la présentation ! Merci de votre coopération.")
				await q.clear_reactions()
				return "done"
			else:
				await q.clear_reactions()
				await q.edit(content = "Vous êtes insatisfait. Si vous souhaitez annuler et supprimer votre présentation, faites `{ctx.prefix}presentation -delete` sur le serveur. \n Si vous souhaitez éditer un champ, faite `{ctx.prefix}presentation -edition [champ à éditer]")
				return "NOTdone"
		return "ERROR"				
	
	async def validation(self, ctx, msg, chartype, member: discord.Member):
		if msg != "error":
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
			c.execute(SQL,(ctx.guild.id))
			channel=c.fetchone()
			def checkValid(reaction, user):
				return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
			if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] != 0):
				chan=tcc.convert(self, ctx, channel[2])
				q=await chan.send (f"Il y a une présentation à valider ! Son contenu est :\n {msg}\n\n Validez-vous la fiche ? ")
				q.add_reaction("✅")
				q.add_reaction("❌")
				reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
				if reaction.emoji=="✅":
					if chartype.lower() == "pnj":
						if channel[1] != 0:
							chan_send=tcc.convert(channel[1])
						else:
							chan_send=tcc.convert(channel[0])
					else:
						chan_send=tcc.convert(channel[0])
					await chan_send.send(msg)
				else:
					await member.send("Il y a un soucis avec votre fiche ! Rapprochez-vous des modérateurs pour voir le soucis.")
			else:
				await member.send ("Huh, il y a eu un soucis avec l'envoie. Il semblerait que les channels ne soient pas configurés ! Rapproche toi du staff pour le prévenir. \n Note : Ce genre de chose n'est pas sensé arrivé, donc contacte aussi @Mara#3000 et fait un rapport de bug. ")

	@commands.command(aliases=["pres"], brief="Commandes pour modifier une présentation en cours.", usage="fiche -(reprise pnj/pj)|(delete pnj/pj)|(edit pj/pnj champ)", help="`fiche -delete` permet de supprimer la présentation en cours. \n `fiche -edit` permet d'éditer un champ d'une présentation en cours. \n `fiche -reprise` permet de reprendre l'écriture d'une présentation en cours. \n Par défaut, les fiches sont des fiches de PJ, donc si vous faites un PNJ, n'oublier pas de le préciser après le nom de la commande !")
	async def fiche (self, ctx, arg, chartype="pj", value="0"):
		member=ctx.message.author
		def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
		c.execute(SQL, (ctx.guild.id))
		channel = c.fetchone()
		if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] !=0):
			if os.path.isfile(f"fiche/{chartype}_{member}.txt"):
				if arg.lower() == "-edit" and value != "0":
					f = open(f"fiche/{chartype}_{member}.txt", "r", encoding="utf-8")
					data = f.readlines()
					f.close()
					f=open(f"fiche/{chartype}_{member}.txt", "w", encoding="utf-8")
					if (len(data) > 0):
						data = "".join(data)
						data = data.replace("\'", "\"")
						perso = json.loads(data)
						if unidecode.unidecode(value.lower()) in perso.keys():
							for k in perso.keys():
								if k == unidecode.unidecode(value.lower()):
									await ctx.send("Regardez vos DM ! 📨 !")
									q = await member.send(f"Par quoi voulez-vous modifier {value.capitalize()} ?\n Actuellement, elle a pour valeur {perso.get(unidecode.unidecode(value.lower()))}.")
									rep = self.bot.wait_for("message", timeout=300, check=checkRep)
									if rep.content.lower() == "stop":
										await q.delete()
										await member.send("Annulation")
										await rep.delete()
										return
									perso[unidecode.unidecode(value.lower())] = rep.content
									f.write(perso)
									q=await q.edit(content="{value.capitalize()} a bien été modifié !")
						else:
							q=await member.send(f"Je n'ai pas trouvé le champ {value.capitalize()}...")
					f.close()
				elif arg.lower() == "-delete":
					os.remove("fiche/{chartype}_{member}.txt")
					await ctx.send("Votre présentation a été supprimé.")
				elif arg.lower() == "-reprise":
					await ctx.send("Regardez vos DM 📨 !")
					step=await self.start_presentation(ctx, member, chartype)
					if step == "done":
						msg=self.forme(chartype)
						await self.validation(ctx, msg, chartype, member)
			else:
				await ctx.send("Vous n'avez pas de présentation en cours !")
		else:
			await ctx.send("Impossible de faire une présentation : Les channels ne sont pas configuré !")
