import discord
from discord.ext import commands
import sqlite3
import copy


class CommandList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def check(self, ctx, *args):

        cmdAuthor = ctx.author
        cmdChannel = None

        LIST_USER_VCUsers : discord.abc.User = list()

        usersNotFound = list()

        # get voice channel the command author is in
        for vChannel in ctx.guild.voice_channels:
            for member in vChannel.members:
                if member.id == cmdAuthor.id:
                    cmdChannel = vChannel

        # if the caller isnt in VC, or the bot cant see the VC
        if cmdChannel is None:
            # TODO: throw an exception or something.
            await ctx.send("Join the voice channel you want to check")
            return

        # get all members in caller's VC
        #for member in cmdChannel.members:
        LIST_USER_VCUsers = cmdChannel.members

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



        #loop through arguments
        for u in LIST_STRING_argumentPlayers:
            INT_userID = None #current arg's player's Discord ID
            #loop through DB's users
            for d in LIST_KAMIUSER_storedUsersList:
                #if a DB user has the Arg's alias, set the ID to be that player
                if d.checkIfAliasExists(u):
                    userIsInVC = False
                    #check VC to make sure the DB user is actually in the VC
                    #TODO: Move this out of storedUsers loop
                    for v in LIST_USER_VCUsers:
                        if v.id == d.getUserID():
                            userIsInVC = True
                    #if he is, set the ID
                    if userIsInVC:
                        print("Alias " + u + " exists")
                        INT_userID = d.getUserID()
            #if the user is not in the DB
            if INT_userID == None:
                print("user ID is None")
                #couldnt find user in DB
                #Check voice channel nicknames for username
                for v in LIST_USER_VCUsers:
                    #if found argument in voice chat
                    if v.nick.lower() == u.lower():
                        print("vc user nick " + v.nick + " == argument nick")
                        INT_userID = v.id
                        newUser = [INT_userID, u]

                        #1 if id exists, 0 if not
                        cursor.execute("select exists (select 1 from users where DiscordID='" + (str)(INT_userID) + "')")
                        #if the user exists in the db, add the new alias to the db
                        if cursor.fetchone()[0] == 1:
                            print("cursor found " + (str)(INT_userID) )
                            cursor.execute("select Aliases from Users where DiscordID = '" + (str)(INT_userID) + "'")
                            aliases = cursor.fetchone()
                            aliases = aliases[0] + "," + u
                            updatedUser = kamiUser([INT_userID, aliases])
                            self.addKamiUserToDB(cursor, updatedUser)
                            print("updated user " + v.nick)
                        #else, make a new db entry
                        else:
                            print("cursor did not find " + (str)(INT_userID))
                            self.addKamiUserToDB(cursor, kamiUser(newUser))
                            print("user " + v.nick + " added to db")


            #If it's still not found
            if INT_userID == None:
                usersNotFound.append(u)
                print("USER " + u + " NOT IN VC")

        #Handle output to original channel
        if len(usersNotFound) == 0:
            await ctx.send("All users found in VC")
        else:
            await ctx.send("Users not found: " + self.listToString(usersNotFound))

        #cleanup DB
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

        #scan guild members to find the arg name
        for m in ctx.guild.members:
            if m.display_name.lower() == STRING_id.lower():
                INT_id = m.id
        #if we havent found the user
        if INT_id == 0:
            print("user " + STRING_id + " not found on server")
            await ctx.send("user " + STRING_id + " not found on server")
            return

        #add all args following [1] as nicknames
        LIST_STRING_nick = list()
        for i in range(1, len(args)):
            LIST_STRING_nick.append(args[i])

        STRING_nicknames = ""
        #transform into a string
        for s in LIST_STRING_nick:
            STRING_nicknames = STRING_nicknames + s + ","
        STRING_nicknames = STRING_nicknames[:-1]

        #create tmp kamiuser object
        tempUser = kamiUser([INT_id, STRING_nicknames])

        # 1 if id exists, 0 if not
        cursor.execute("select exists (select 1 from users where DiscordID='" + (str)(INT_id) + "')")
        #if user is already in the db, add new aliases
        if cursor.fetchone()[0] == 1:
            cursor.execute("select Aliases from Users where DiscordID = '" + (str)(INT_id) + "'")
            aliases = cursor.fetchone()
            aliases = aliases[0] + "," + STRING_nicknames
            updatedUser = kamiUser([INT_id, aliases])
            self.addKamiUserToDB(cursor, updatedUser)
            print("updated user " + STRING_id)
        #else create new entry
        else:
            self.addKamiUserToDB(cursor, kamiUser(tempUser))
            print("user " + STRING_id + " added to db")

        #cleanup DB
        conn.commit()
        cursor.close()
        conn.close()


    #Transform list into formatted string
    def listToString(self, s):
        output = ""
        for x in s:
            output = output + (str)(x) + ","
        return output[:-1]


    #Update or Add kamiUser to DB
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
