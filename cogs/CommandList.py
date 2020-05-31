import discord
from discord.ext import commands
import sqlite3
import copy
from Database import Database


class CommandList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database('data/namesDB.db')

    @commands.command()
    async def check(self, ctx, *args):

        if len(args) == 0:
            await ctx.send("Usage: *check Player1, Player2, Player3, ... , PlayerN")
            return

        cmdAuthor = ctx.author
        cmdChannel = None
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
        vcUsers = cmdChannel.members

        #All users currently in the DB
        lines = self.db.getAllDBUsers()

        # parse all lines into kamiUsers
        storedUsers = list()
        for line in lines:
            storedUsers.append(kamiUser(line))

        #store args into list
        argumentPlayers = list()
        for arg in args:
            argumentPlayers.append(arg.replace(",",""))

        #loop through arguments
        for argPlayer in argumentPlayers:
            userID = None #current arg's player's Discord ID
            #loop through DB's users
            for storedUser in storedUsers:
                #if a DB user has the Arg's alias, set the ID to be that player
                if storedUser.checkIfAliasExists(argPlayer):
                    userIsInVC = False
                    #check VC to make sure the DB user is actually in the VC
                    #TODO: Move this out of storedUsers loop
                    for vcUser in vcUsers:
                        if (str)(vcUser.id) == (str)(storedUser.getUserID()):
                            userIsInVC = True
                    #if he is, set the ID
                    if userIsInVC:
                        print("Alias " + argPlayer + " exists")
                        userID = storedUser.getUserID()

            #if the user is not in the DB
            if userID == None:
                print("user ID is None")
                #couldnt find user in DB
                #Check voice channel nicknames for username
                for vcUser in vcUsers:
                    #if found argument in voice chat
                    if vcUser.nick.lower() == argPlayer.lower():
                        print("vc user nick " + vcUser.nick + " == argument nick")
                        self.addOrUpdateUserToDB(vcUser.id, argPlayer)
            #If it's still not found
            if userID == None:
                usersNotFound.append(argPlayer)
                print("USER " + argPlayer + " NOT IN VC")

        #Handle output to original channel
        if len(usersNotFound) == 0:
            await ctx.send("All users found in VC")
        else:
            await ctx.send("Users not found: " + self.listToString(usersNotFound))

        #cleanup DB
        #self.db.writeChanges()
        #TODO: Eventually actually close this
        #self.db.closeDB()

    @commands.command()
    async def add(self, ctx, *args):

        if len(args) == 0:
            await ctx.send("Usage: *add DiscordName Alias1 Alias2 Alias3 ... AliasN")
            return


        STRING_id = args[0]
        INT_id = 0

        #scan guild members to find the arg name
        for member in ctx.guild.members:
            if member.display_name.lower() == STRING_id.lower():
                INT_id = member.id
        #if we havent found the user
        if INT_id == 0:
            print("user " + STRING_id + " not found on server")
            await ctx.send("user " + STRING_id + " not found on server")
            return

        #add all args following [1] as nicknames
        nicknames = list()
        for i in range(1, len(args)):
            nicknames.append(args[i])

        #TODO: Make this not retarded
        strNicknames = ""
        #transform into a string
        for nickname in nicknames:
            strNicknames = strNicknames + nickname + ","
        strNicknames = strNicknames[:-1]

        self.addOrUpdateUserToDB(INT_id, strNicknames)

        await ctx.send("Nickname(s) " + strNicknames + " added to user " + args[0])

        #TODO: Eventually close this
        #self.db.closeDB()

    def addOrUpdateUserToDB(self, id, oldNicknames):
        if self.db.getExistsUserID(id) == 1:
            aliases = self.db.getDBUserAliasesByID(id)
            aliases = aliases[0] + "," + oldNicknames
            updatedUser = kamiUser([id, aliases])
            self.db.addKamiUserToDB(updatedUser)
        #else create new entry
        else:
            self.db.addKamiUserToDB(kamiUser([id, oldNicknames]))

    #Transform list into formatted string
    def listToString(self, s):
        output = ""
        for x in s:
            output = output + (str)(x) + ","
        return output[:-1]


class kamiUser(object):
    userID = None
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
