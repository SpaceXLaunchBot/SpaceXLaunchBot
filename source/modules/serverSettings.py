class serverSettingsObj(object):
    def __init__(self, serverID, cmdPrefix="!", launchingSoonPings=None):
        self.ID = serverID
        self.cmdPrefix = cmdPrefix
        # The mentions to ping when a "launching soon" notif is sent
        self.launchingSoonPings = launchingSoonPings
