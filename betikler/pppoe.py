#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import popen2
import os

class pppoe:
    """ Functions to configure and run PPP over Ethernet connections  """

    tmpl_pppoe_conf = """
#***********************************************************************
#
# /etc/ppp/pppoe.conf
#
# Configuration file for rp-pppoe.
#
# NOTE: This file is used by the adsl-start, adsl-stop, adsl-connect and
#       adsl-status shell scripts.  It is *not* used in any way by the
#       "pppoe" executable.
#
#***********************************************************************

# When you configure a variable, DO NOT leave spaces around the "=" sign.

# Ethernet card connected to ADSL modem
ETH=\"%s\"

# ADSL user name.  You may have to supply "@provider.com"  Sympatico
# users in Canada do need to include "@sympatico.ca"
# Sympatico uses PAP authentication.  Make sure /etc/ppp/pap-secrets
# contains the right username/password combination.
# For Magma, use xxyyzz@magma.ca
USER=\"%s\"

# Bring link up on demand?  Default is to leave link up all the time.
# If you want the link to come up on demand, set DEMAND to a number indicating
# the idle time after which the link is brought down.
DEMAND=no
#DEMAND=300

# DNS type: SERVER=obtain from server; SPECIFY=use DNS1 and DNS2;
# NOCHANGE=do not adjust.
DNSTYPE=COMAR

# Obtain DNS server addresses from the peer (recent versions of pppd only)
# In old config files, this used to be called USEPEERDNS.  Changed to
# PEERDNS for better Red Hat compatibility
PEERDNS=yes

DNS1=
DNS2=

# Make the PPPoE connection your default route.  Set to
# DEFAULTROUTE=no if you don't want this.
DEFAULTROUTE=yes

### ONLY TOUCH THE FOLLOWING SETTINGS IF YOU'RE AN EXPERT

# How long adsl-start waits for a new PPP interface to appear before
# concluding something went wrong.  If you use 0, then adsl-start
# exits immediately with a successful status and does not wait for the
# link to come up.  Time is in seconds.
#
# WARNING WARNING WARNING:
#
# If you are using rp-pppoe on a physically-inaccessible host, set
# CONNECT_TIMEOUT to 0.  This makes SURE that the machine keeps trying
# to connect forever after adsl-start is called.  Otherwise, it will
# give out after CONNECT_TIMEOUT seconds and will not attempt to
# connect again, making it impossible to reach.
CONNECT_TIMEOUT=30

# How often in seconds adsl-start polls to check if link is up
CONNECT_POLL=2

# Specific desired AC Name
ACNAME=

# Specific desired service name
SERVICENAME=

# Character to echo at each poll.  Use PING="" if you don't want
# anything echoed
PING="."

# File where the adsl-connect script writes its process-ID.
# Three files are actually used:
#   $PIDFILE       contains PID of adsl-connect script
#   $PIDFILE.pppoe contains PID of pppoe process
#   $PIDFILE.pppd  contains PID of pppd process
#
# PIDFILE="/var/run/$CF_BASE-adsl.pid"
PIDFILE="/var/run/adsl.pid"

# Do you want to use synchronous PPP?  "yes" or "no".  "yes" is much
# easier on CPU usage, but may not work for you.  It is safer to use
# "no", but you may want to experiment with "yes".  "yes" is generally
# safe on Linux machines with the n_hdlc line discipline; unsafe on others.
SYNCHRONOUS=no

# Do you want to clamp the MSS?  Here's how to decide:
# - If you have only a SINGLE computer connected to the ADSL modem, choose
#   "no".
# - If you have a computer acting as a gateway for a LAN, choose "1412".
#   The setting of 1412 is safe for either setup, but uses slightly more
#   CPU power.
CLAMPMSS=1412
#CLAMPMSS=no

# LCP echo interval and failure count.
LCP_INTERVAL=20
LCP_FAILURE=3

# PPPOE_TIMEOUT should be about 4*LCP_INTERVAL
PPPOE_TIMEOUT=80

# Firewalling: One of NONE, STANDALONE or MASQUERADE
FIREWALL=NONE

# Linux kernel-mode plugin for pppd.  If you want to try the kernel-mode
# plugin, use LINUX_PLUGIN=rp-pppoe.so
LINUX_PLUGIN=

# Any extra arguments to pass to pppoe.  Normally, use a blank string
# like this:
PPPOE_EXTRA=""

# Rumour has it that "Citizen's Communications" with a 3Com
# HomeConnect ADSL Modem DualLink requires these extra options:
# PPPOE_EXTRA="-f 3c12:3c13 -S ISP"

# Any extra arguments to pass to pppd.  Normally, use a blank string
# like this:
PPPD_EXTRA=""


########## DON'T CHANGE BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
# If you wish to COMPLETELY overrride the pppd invocation:
# Example:
# OVERRIDE_PPPD_COMMAND="pppd call dsl"

# If you want adsl-connect to exit when connection drops:
# RETRY_ON_FAILURE=no
"""
    
    tmpl_options = """
noipdefault
hide-password
defaultroute
persist
lock
"""

    def silentUnlink(self, path):
        """ Try to unlink a file, if exists """

        try:
            os.unlink(path)
        except:
            pass

    def capture(self, cmd):
        """ Run a command and capture the output """

        out = []
        a = popen2.Popen4(cmd)
        while 1:
            b = a.fromchild.readline()
            if b == None or b == "":
                break
            out.append(b)
        return (a.wait(), out)

    def getDNS(self):
        """ Try to get DNS server adress provided by remote peer """

        list = []
        try:
            f = open("/etc/ppp/resolv.conf", "r")
            for line in f.readlines():
                if line.strip().startswith("nameserver"):
                    list.append(line[line.find("nameserver") + 10:].rstrip('\n').strip())
            f.close()
        except IOError:
            return None

        return list

    def createConf(self, dev, user):
        """ Create configuration file for pppoe connections """

        self.silentUnlink("/etc/ppp/pppoe.conf")
        try:
            f = open("/etc/ppp/pppoe.conf", "w")
            f.write(self.tmpl_pppoe_conf % (dev, user))
            f.close()
        except:
            return True

        return None

    def createOptions(self):
        """ Create options file for pppoe connections """

        self.silentUnlink("/etc/ppp/options-pppoe")
        try:
            f = open("/etc/ppp/options-pppoe", "w")
            f.write(self.tmpl_options)
            f.close()
        except:
            return True

        return None

    def createSecrets(self, user, pwd):
        """ Create authentication files """

        try:
            # Ugly way to clean up secrets and recreate
            self.silentUnlink("/etc/ppp/pap-secrets")
            self.silentUnlink("/etc/ppp/chap-secrets")
            f = os.open("/etc/ppp/pap-secrets", os.O_CREAT, 0o600)
            os.close(f)
            os.symlink("/etc/ppp/pap-secrets", "/etc/ppp/chap-secrets")
        except:
            return True
            
        f = open("/etc/ppp/pap-secrets", "w")
        data = "\"%s\" * \"%s\"\n" % (user, pwd)
        f.write(data)
        f.close()

        return None

    def getStatus(self):
        """ Stop the pppoe connection """

        cmd = "/usr/sbin/adsl-status"
        i, output = self.capture(cmd)

        return output

    def stopPPPD(self):
        """ Stop the pppoe connection """

        cmd = "/usr/sbin/adsl-stop"
        i, output = self.capture(cmd)

        return output

    def startPPPD(self):
        """ Start the PPP daemon """

        cmd = "/usr/sbin/adsl-start"
        i, output = self.capture(cmd)

        return output

    def connect(self, dev, user, pwd):
        """ Try to start a pppoe connection through dev and login """
    
        if self.createConf(dev, user) is True:
            return "Could not manage pppoe configuration"

        if self.createOptions() is True:
            return "Could not manage pppd parameters"

        if self.createSecrets(user, pwd) is True:
            return "Could not manage authentication files"

        output = self.startPPPD()
        return output

if __name__ == "__main__":
    rp = pppoe()
    rp.connect("eth0", "parbusman@uludag", "pek gizli")

