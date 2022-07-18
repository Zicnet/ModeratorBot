import datetime
import string, json
import discord
import sqlite3 as sq
from discord.ext import commands
from datetime import timedelta, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


bot = commands.Bot(command_prefix='.')

with sq.connect('DataBase.db') as con:
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS warn ( 
        id INTEGER PRIMARY KEY,
        userid INT, 
        moderid INT,
        reason TEXT,
        time TEXT,
        activ BLOB DEFAULT TRUE,   
        time_out TEXT
        )""")

@bot.command()
async def warnlist(ctx, opponent: discord.Member):
    searchuser = opponent.id
    member = ctx.message.author
    cur.execute(f"SELECT id, moderid, reason, time, activ FROM warn WHERE(userid = {searchuser})")
    record = cur.fetchall()
    if len(record) == 0:
        await ctx.send(embed = discord.Embed(title = 'Кол-во Предупреждение', description=f"У {opponent.mention} `0` варнов",colour = discord.Colour.from_rgb(66,63,246)))
        return
    embed = discord.Embed(title = f"Варны {opponent}", colour=discord.Colour.from_rgb(246,14,34))
    for i in record:
        id = i[0]
        moderid = i[1]
        reason = i[2]
        date = i[3]
        active = i[4]
        if active == 1:
            active = "Активный"
        else:
            active = "Неактивный"
        embed.add_field(name=f"ID {id} - {active}", value=f"Дата выдачи: {date} | Причина: {reason}", inline=False)
    await ctx.channel.send(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    date = datetime.now()
    member = message.author
    date_now = datetime.now()
    date_out = date_now + timedelta(minutes=15)
    data_print = datetime.strftime(date_out, "%d/%m/%y")
    role = discord.utils.get(member.guild.roles, id=931231654641549364)
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')} \
    .intersection(set(json.load(open('banwolrd.json')))) != set():
        await message.delete()
        cur.execute(f"SELECT * FROM warn WHERE userid = {member.id}")
        record = cur.fetchall()
        if len(record) < 2:
            cur.execute(f"INSERT INTO warn(userid, moderid, reason, time ) VALUES({member.id}, 0,'banworld' ,'{date_out}')")
            con.commit()
            await message.channel.send(
                embed = discord.Embed(
                    title="Предупреждение",
                    description=f"{message.author.mention}, это `{len(record) + 1}` предупреждение",
                    colour=discord.Colour.from_rgb(246,14,34)
                    ))
            await message.channel.send(
                embed=discord.Embed(
                    title="Предупреждение",
                    description=f" Ууу за такое можно и в бан отлететь, {member.mention}. А пока подумай о своем поведении и вернись к нам `{data_print}`",
                    colour=discord.Colour.from_rgb(246, 14, 34)
                ))
        if len(record) >= 2:
            cur.execute(f"INSERT INTO warn(userid, moderid, reason, time, time_out  ) VALUES({member.id}, 0,'banworld' ,'{date}','{data_print}')")
            con.commit()
            await message.channel.send(
                embed=discord.Embed(
                    title="Наказание",
                    description=f"Выдан мут {member.mention}",
                    colour=discord.Colour.from_rgb(246, 14, 34)
                    ))
            await message.channel.send(
                embed=discord.Embed(
                    title="Наказание",
                    description=f"{member.mention}, пока подумай о своем поведении и вернись к нам `{date_out}`",
                    colour=discord.Colour.from_rgb(246, 14, 34)
                ))
            await member.add_roles(role)

@bot.command()
async def warnset(ctx, opponent: discord.Member, time: int, hd: str, *,text: str):
    member = ctx.author
    cur.execute(f"SELECT * FROM warn WHERE userid= {opponent.id} AND activ=1")
    record = cur.fetchall()
    role = discord.utils.get(opponent.guild.roles, id=931231654641549364)
    if hd == 'h':
        date_now = datetime.now()
        date_out = date_now + timedelta(hours=time)
    elif hd == 'd':
        date_now = datetime.now()
        date_out = date_now + timedelta(days=time)
    elif hd == 'm':
        date_now = datetime.now()
        date_out = date_now + timedelta(minutes=time)
    else:
        date_now = datetime.now()
        date_out = 0
    data_print = datetime.strftime(date_out, "%d/%m/%y %H:%M")
    cur.execute(f"INSERT INTO warn(userid, moderid, reason, time, time_out ) VALUES({opponent.id}, {member.id},'{text}' ,'{date_now}', '{date_out}')")
    con.commit()
    if len(record) >= 4:
        await ctx.channel.send(
            embed=discord.Embed(
                title="Наказание",
                description=f"Выдан мут {opponent.mention}, срок которого истечёт `{data_print}`",
                colour=discord.Colour.from_rgb(246, 14, 34)
            ))
        await opponent.add_roles(role)
    if len(record) < 4:
        await ctx.channel.send(
            embed=discord.Embed(
                title="Предупреждение",
                description=f"{member.mention}, выдал предупреждение {opponent.mention}, срок которого истечёт `{data_print}`",
                colour=discord.Colour.from_rgb(246, 14, 34)
            ))

@bot.command()
async def warnremove(ctx, id: int):
    cur.execute(f"UPDATE warn SET activ = 0 WHERE id = {id}")
    con.commit()
    member = ctx.author
    record = cur.fetchall()
    if len(record):
        await ctx.channel.send(
            embed=discord.Embed(
                title="Уведомление",
                description=f"{member.mention}, cнял предупреждение",
                colour=discord.Colour.from_rgb(246, 14, 34)
            ))

async def warntime():
    print('test')

@bot.event
async def on_ready():
    print(f'{datetime.now()} ON READY')
    await bot.change_presence( status= discord.Status.online , activity= discord.Game('Zicnet'))

    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(warntime, trigger='cron',hour= 18,minute=22)
    scheduler.start()

print(f'{datetime.now()} BOT START')
bot.run('OTI3OTkwNDg3OTkyOTI2MjY4.YdSQfQ.FGFnnQbyxRLuS-5OKSYm7Hx1O8o')