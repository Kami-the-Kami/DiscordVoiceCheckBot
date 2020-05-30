import discord
from discord.ext import commands
import sqlite3
import copy


class CommandList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def check(self, ctx, *args):

        USER_author = ctx.author
        CHANNEL_channel = None
        #args = ctx.args

        LIST_USER_VCUsers : discord.abc.User = list()

        usersNotFound = list()

        # get voice channel the command author is in
        for c in ctx.guild.voice_channels:
            for m in c.members:
                if m.id == USER_author.id:
                    CHANNEL_channel = c

        # if the caller isnt in VC, or the bot cant see the VC
        if CHANNEL_channel is None:
            # TODO: throw an exception or something.
            await ctx.send("Join the voice channel you want to check")
            return

        # get all members in caller's VC
        #TODO: switch this to an assign statement once known it works
        for m in CHANNEL_channel.members:
            LIST_USER_VCUsers.append(m)

        # set up DB, lines is all users in VC
        # TODO: Move this somewhere where cursor isn't queried >1 times
        conn = sqlite3.connect('data/namesDB.db')
        cursor = conn.cursor()
        cursor.execute("select * from Users")
        lines = cursor.fetchall()


        # parse all lines into kamiUsers
        LIST_KAMIUSER_storedUsersList: kamiUser = list()
        for l in lines:
            x = copy.copy(kamiUser(l))
            LIST_KAMIUSER_storedUsersList.append(x)

        #store args into list
        LIST_STRING_argumentPlayers = list()
        for p in args:
            LIST_STRING_argumentPlayers.append(p.replace(",",""))


        #check each discordID in db against
        for u in LIST_STRING_argumentPlayers:
            INT_userID = None
            for d in LIST_KAMIUSER_storedUsersList:
                if d.checkIfAliasExists(u):
                    print("Alias " + u + " exists")
                    INT_userID = d.getUserID()
            if INT_userID == None:
                print("user ID is None")
                #couldnt find user in DB
                #Check voice channel nicknames for username
                for v in LIST_USER_VCUsers:
                    if v.nick.lower() == u.lower():
                        print("vc user nick " + v.nick + " == argument nick")
                        INT_userID = v.id
                        newUser = [INT_userID, u]

                        #1 if id exists, 0 if not
                        cursor.execute("select exists (select 1 from users where DiscordID='" + (str)(INT_userID) + "')")
                        if cursor.fetchone()[0] == 1:
                            print("cursor found " + (str)(INT_userID) )
                            cursor.execute("select Aliases from Users where DiscordID = '" + (str)(INT_userID) + "'")
                            aliases = cursor.fetchone()
                            aliases = aliases[0] + "," + u
                            updatedUser = kamiUser([INT_userID, aliases])
                            self.addKamiUserToDB(cursor, updatedUser)
                            print("updated user " + v.nick)
                        else:
                            print("cursor did not find " + (str)(INT_userID))
                            self.addKamiUserToDB(cursor, kamiUser(newUser))
                            print("user " + v.nick + " added to db")


            #If it's still not found
            if INT_userID == None:
                usersNotFound.append(u)
                print("USER " + u + " NOT IN VC")

        if len(usersNotFound) == 0:
            await ctx.send("All users found in VC")
        else:
            await ctx.send("Users not found: " + self.listToString(usersNotFound))


        conn.commit()
        cursor.close()
        conn.close()

    @commands.command()
    async def add(self, ctx, *args):
        # set up DB, lines is all users in VC
        # TODO: Move this somewhere where cursor isn't queried >1 times
        conn = sqlite3.connect('data/namesDB.db')
        cursor = conn.cursor()

        STRING_id = args[0]
        INT_id = 0

        for m in ctx.guild.members:
            print("---")
            print(m)
            print(m.nick)
            print(m.display_name)
            print(m.id)
            if m.display_name.lower() == STRING_id.lower():
                INT_id = m.id

        if INT_id == 0:
            print("user " + STRING_id + " not found on server")
            await ctx.send("user " + STRING_id + " not found on server")
            return


        LIST_STRING_nick = list()
        for i in range(1, len(args)):
            LIST_STRING_nick.append(args[i])

        STRING_nicknames = ""
        for s in LIST_STRING_nick:
            STRING_nicknames = STRING_nicknames + s + ","
        STRING_nicknames = STRING_nicknames[:-1]

        tempUser = kamiUser([INT_id, STRING_nicknames])

        # 1 if id exists, 0 if not
        cursor.execute("select exists (select 1 from users where DiscordID='" + (str)(INT_id) + "')")
        if cursor.fetchone()[0] == 1:
            cursor.execute("select Aliases from Users where DiscordID = '" + (str)(INT_id) + "'")
            aliases = cursor.fetchone()
            aliases = aliases[0] + "," + STRING_nicknames
            updatedUser = kamiUser([INT_id, aliases])
            self.addKamiUserToDB(cursor, updatedUser)
            print("updated user " + STRING_id)
        else:
            self.addKamiUserToDB(cursor, kamiUser(tempUser))
            print("user " + STRING_id + " added to db")

        conn.commit()
        cursor.close()
        conn.close()



    def listToString(self, s):
        output = ""
        for x in s:
            output = output + (str)(x) + ","
        return output[:-1]



    def addKamiUserToDB(self, cursor, kUser):
        print(kUser.getUserID())
        print(kUser.getAliasesAsString())
        cursor.execute("insert or replace into Users (DiscordID, Aliases) values ('" + (str)(kUser.getUserID()) + "','" + kUser.getAliasesAsString() +"')")















class kamiUser(object):
    userID : str= None
    aliases = list()

    def __init__(self, line):
        self.lines = line

        self.setUserID(line[0])
        self.setAliases(line[1])

    def getUserID(self):
        return self.userID

    def getAliasesAsList(self):
        return self.aliases

    def getAliasesAsString(self):
        str = ""
        for a in self.aliases:
            str = str + a + ","
        return str[:-1]


    def setUserID(self, id):
        self.userID = id


    def setAliases(self, lines):
        self.aliases = lines.replace(" ","").split(",")
        
    def setAliasesFromList(self, lst):
        self.aliases = lst



    def checkIfAliasExists(self, alias):
        for a in self.getAliasesAsList():
            if a.lower() == alias.lower():
                return True
        return False

























def setup(bot):
    bot.add_cog(CommandList(bot))
