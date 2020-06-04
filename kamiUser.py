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
        self.aliases = lines.replace(" ", "").split(",")

    def setAliasesFromList(self, lst):
        self.aliases = lst

    def checkIfAliasExists(self, alias):
        for a in self.getAliasesAsList():
            if a.lower() == alias.lower():
                return True
        return False
