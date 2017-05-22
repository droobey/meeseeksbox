# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Carry out voice commands by recognising keywords."""

import datetime
import logging
import subprocess

import actionbase

import os
import json
import random

import requests


# =============================================================================
#
# Hey, Makers!
#
# This file contains some examples of voice commands that are handled locally,
# right on your Raspberry Pi.
#
# Do you want to add a new voice command? Check out the instructions at:
# https://aiyprojects.withgoogle.com/voice/#makers-guide-3-3--create-a-new-voice-command-or-action
# (MagPi readers - watch out! You should switch to the instructions in the link
#  above, since there's a mistake in the MagPi instructions.)
#
# In order to make a new voice command, you need to do two things. First, make a
# new action where it says:
#   "Implement your own actions here"
# Secondly, add your new voice command to the actor near the bottom of the file,
# where it says:
#   "Add your own voice commands here"
#
# =============================================================================

# Actions might not use the user's command. pylint: disable=unused-argument


# Example: Say a simple response
# ================================
#
# This example will respond to the user by saying something. You choose what it
# says when you add the command below - look for SpeakAction at the bottom of
# the file.
#
# There are two functions:
# __init__ is called when the voice commands are configured, and stores
# information about how the action should work:
#   - self.say is a function that says some text aloud.
#   - self.words are the words to use as the response.
# run is called when the voice command is used. It gets the user's exact voice
# command as a parameter.

class SpeakAction(object):

    """Says the given text via TTS."""

    def __init__(self, say, words):
        self.say = say
        self.words = words

    def run(self, voice_command):
        self.say(self.words)


# Example: Tell the current time
# ==============================
#
# This example will tell the time aloud. The to_str function will turn the time
# into helpful text (for example, "It is twenty past four."). The run function
# uses to_str say it aloud.

class SpeakTime(object):

    """Says the current local time with TTS."""

    def __init__(self, say):
        self.say = say

    def run(self, voice_command):
        time_str = self.to_str(datetime.datetime.now())
        self.say(time_str)

    def to_str(self, dt):
        """Convert a datetime to a human-readable string."""
        HRS_TEXT = ['midnight', 'one', 'two', 'three', 'four', 'five', 'six',
                    'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
        MINS_TEXT = ["five", "ten", "quarter", "twenty", "twenty-five", "half"]
        hour = dt.hour
        minute = dt.minute

        # convert to units of five minutes to the nearest hour
        minute_rounded = (minute + 2) // 5
        minute_is_inverted = minute_rounded > 6
        if minute_is_inverted:
            minute_rounded = 12 - minute_rounded
            hour = (hour + 1) % 24

        # convert time from 24-hour to 12-hour
        if hour > 12:
            hour -= 12

        if minute_rounded == 0:
            if hour == 0:
                return 'It is midnight.'
            return "It is %s o'clock." % HRS_TEXT[hour]

        if minute_is_inverted:
            return 'It is %s to %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])
        return 'It is %s past %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])


# Example: Run a shell command and say its output
# ===============================================
#
# This example will use a shell command to work out what to say. You choose the
# shell command when you add the voice command below - look for the example
# below where it says the IP address of the Raspberry Pi.

class SpeakShellCommandOutput(object):

    """Speaks out the output of a shell command."""

    def __init__(self, say, shell_command, failure_text):
        self.say = say
        self.shell_command = shell_command
        self.failure_text = failure_text

    def run(self, voice_command):
        output = subprocess.check_output(self.shell_command, shell=True).strip()
        if output:
            self.say(output.decode('utf-8'))
        elif self.failure_text:
            self.say(self.failure_text)


# Example: Change the volume
# ==========================
#
# This example will can change the speaker volume of the Raspberry Pi. It uses
# the shell command SET_VOLUME to change the volume, and then GET_VOLUME gets
# the new volume. The example says the new volume aloud after changing the
# volume.

class VolumeControl(object):

    """Changes the volume and says the new level."""

    GET_VOLUME = r'amixer get Master | grep "Front Left:" | sed "s/.*\[\([0-9]\+\)%\].*/\1/"'
    SET_VOLUME = 'amixer -q set Master %d%%'

    def __init__(self, say, change):
        self.say = say
        self.change = change

    def run(self, voice_command):
        res = subprocess.check_output(VolumeControl.GET_VOLUME, shell=True).strip()
        try:
            logging.info("volume: %s", res)
            vol = int(res) + self.change
            vol = max(0, min(100, vol))
            subprocess.call(VolumeControl.SET_VOLUME % vol, shell=True)

            self.say(_('Volume at %d %%.') % vol)
        except (ValueError, subprocess.CalledProcessError):
            logging.exception("Error using amixer to adjust volume.")


# Example: Repeat after me
# ========================
#
# This example will repeat what the user said. It shows how you can access what
# the user said, and change what you do or how you respond.

class RepeatAfterMe(object):

    """Repeats the user's command."""

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):
        # The command still has the 'repeat after me' keyword, so we need to
        # remove it before saying whatever is left.
        to_repeat = voice_command.replace(self.keyword, '', 1)
        self.say(to_repeat)


# =========================================
# Makers! Implement your own actions here.
# =========================================

#This works by rolling a number between 1 and whatever you want.
#There will be the chance of 1/your number to play a either one of two wavs
#If the random number rolled isn't one it will play <keyword>.wav from the wavs/chance folder
#It will then -1 from your number (total chance) and save it to a file
#If it IS 1 it will play <keyword>-full.wav wavs/chance folder
#It will then reset the chance back to default
#
#e.g.  actor.add_keyword(_('command'), WavChance(say,"moonmen", 10))
# has a 1/10 chance of playing moonmen-full.wav or moonmen.wav

class WavChance(object):
    def __init__(self,say,keyword,chanc=10):
        self.say = say
        self.path = "../wavs/chance/"+str(keyword)
        self.chance = str(chanc)
    def run(self, command):
        import os,random
        if os.path.isfile("../wavs/chance/chance-"+os.path.basename(self.path)):
            with open("../wavs/chance/chance-"+os.path.basename(self.path),"r") as f:
                chance=int(f.read().strip())
        else:
            f=open("../wavs/chance/chance-"+os.path.basename(self.path),"w")
            f.write(str(self.chance))
            f.close()
            chance=self.chance
        logging.debug("Current chance: "+str(chance))
        r=random.randint(1,chance)
        logging.debug("1/"+str(chance)+", rolled a "+str(r))
        if r == 1:
            #ding,ding,ding,jackpot!
            os.system("aplay "+self.path+"-full.wav")
            with open("../wavs/chance/chance-"+os.path.basename(self.path),"w") as f:
                f.write(str(self.chance))
        else:
            os.system("aplay "+self.path+".wav")
            chance=chance-1
            with open("../wavs/chance/chance-"+os.path.basename(self.path),"w") as f:
                f.write(str(chance))
            
class PlayWav(object):
    def __init__(self,say,keyword):
        self.say = say
        self.path = keyword
    def run(self, command):
        os.system("aplay "+self.path)

#choose a random TV Show!
class EpisodeRandom(object):
    def __init__(self,say,keyword):
        self.say=say
        self.keyword=keyword
        #Put your TVDB API KEY here!
        #Get API key here http://thetvdb.com/?tab=apiregister
        self.api_key="TVDBAPIKEY"
        
    def grab_tvdb(self,id):
        import tvdb
        tv=tvdb.tvdb(self.api_key,id)
        page=1
        maxpage=1
        try:
            s=tv.GET("series/"+str(id)+"/episodes?page="+str(page))
        except:
            self.say("I couldn't connect to the TV database. Have you set your API key correctly?")
            return False
        maxpage=s["links"]["last"]+1
        o=[]
        o.extend(s["data"])
        for i in range (2, maxpage):
            s=tv.GET("series/"+str(id)+"/episodes?page="+str(i))
            o.extend(s["data"])

        return {"episodes":o}
    
    def grab_tvdb_show(self,show):
        import tvdb
        #Get API key here http://thetvdb.com/?tab=apiregister
        tv=tvdb.tvdb(self.api_key) #Put your TVDB API KEY here!
        try:
            s=tv.GET("search/series?name="+str(show))
            return s["data"][0]
        except:
            self.say("I couldn't connect to the TV database. Have you set your API key correctly?")
            return False
    def run(self, command):

        random.seed()
        
        #Put your favourite TV Shows here
        #You'll need its tvdb_id, just search it on thetvdb.com
        #It will be in the URL e.g. http://thetvdb.com/?tab=series&id=IDHERE
        
        #list  =  [[showname,the_tvdb_id],....]
        shows=[["Futurama",73871],
        ["Rick and Morty",275274]]

        from time import time,sleep 
        if not self.keyword == "episodeof":
            c=random.choice(shows)
        else:
            show=command.replace("suggest random episode of","").strip()
            show=show.replace("random episode of","").strip()
            get_show=self.grab_tvdb_show(show)
            if not get_show:
                self.say("Sorry, I can't seem to find "+str(show)+" on the TV database")
                return
            else:
                c=[get_show["seriesName"],get_show["id"]]
                
            
        cachepath="tvdb_cache/tvdb_"+str(c[1])+".json"
        if os.path.isfile(cachepath):
            with open(cachepath) as data_file:
                data = json.load(data_file)
            if int(data["updated"])+604800 < time():
                #out of date
                o = self.grab_tvdb(c[1])
                if not o:
                    return False
                o["updated"]=time()
                with open(cachepath, 'w') as outfile:
                    json.dump(o,outfile)
                showeps=o
            else:
                #up to date
                with open(cachepath) as data_file:
                    showeps=json.load(data_file)
        else:
            #new file
            o = self.grab_tvdb(c[1])
            o["updated"]=time()
            with open(cachepath, 'w') as outfile:
                json.dump(o,outfile)
            showeps=o

        while True:
            ep=random.choice(showeps["episodes"])
            if not ep['airedSeason'] == 0:
                break
                
                
        intro=["How about","Try","You should watch","Have a look at","You may like"]
        self.say(random.choice(intro)+" "+c[0]+"      Season "+str(ep['airedSeason'])+" Episode "+str(ep['airedEpisodeNumber'])+" "+ep['episodeName'])

def make_actor(say):
    """Create an actor to carry out the user's commands."""

    actor = actionbase.Actor()

    actor.add_keyword(
        _('ip address'), SpeakShellCommandOutput(
            say, "ip -4 route get 1 | head -1 | cut -d' ' -f8",
            _('I do not have an ip address assigned to me.')))

    actor.add_keyword(_('volume up'), VolumeControl(say, 10))
    actor.add_keyword(_('volume down'), VolumeControl(say, -10))
    actor.add_keyword(_('max volume'), VolumeControl(say, 100))

    actor.add_keyword(_('repeat after me'),
                      RepeatAfterMe(say, _('repeat after me')))

    # =========================================
    # Makers! Add your own voice commands here.
    # =========================================
    
    
    #read config
    
    #Edit the file called cmd-config 
    #Layout
    #parrot=Voom,Norwegian Blue,4000000
    #  ^      ^        ^              ^
    #Command  |        |              |
    #       Class  Keyword   Extra Parameter
    
    
    with open("cmd-config","r") as f:
        for line in f:
           line=line.strip()
           if line[0]=="#":  #comment, ingore this line
               continue
           cmd=line.split("=",1)
           module=cmd[1].split(",",3)
           kword=module[1]

           try:
               cl=globals()[module[0]]
               
               if len(module)>2:
                    actor.add_keyword(_( cmd[0].strip() ), cl(say,kword,module[2])) 
                   
               else:
                    actor.add_keyword(_( cmd[0].strip() ), cl(say,kword)) 
               logging.debug("Added command from config - "+str(cmd[0])+" ("+module[0]+")")
           except:
               import traceback,sys
               exc_type, exc_value, exc_traceback = sys.exc_info()
               logging.debug("Failed to add command from config - "+str(cmd[0])+" ("+module[0]+")")  
               traceback.print_exc()
               
           

    actor.add_keyword(_('what is your purpose'),
                     SpeakAction(say, _("I pass butter")))
                     
    #start random episode
    #Look in the EpisodeRandom function for setup!
    actor.add_keyword(_("suggest random episode of"),
                      EpisodeRandom(say,_("episodeof")))
    actor.add_keyword(_("random episode"),
                      EpisodeRandom(say,_("episode")))
    actor.add_keyword(_("random episode of"),
                      EpisodeRandom(say,_("episodeof")))
    #end random episode

    return actor


def add_commands_just_for_cloud_speech_api(actor, say):
    """Add simple commands that are only used with the Cloud Speech API."""
    def simple_command(keyword, response):
        actor.add_keyword(keyword, SpeakAction(say, response))

    simple_command('alexa', _("We've been friends since we were both starter projects"))
    simple_command(
        'beatbox',
        'pv zk pv pv zk pv zk kz zk pv pv pv zk pv zk zk pzk pzk pvzkpkzvpvzk kkkkkk bsch')
    simple_command(_('clap'), _('clap clap'))
    simple_command('google home', _('She taught me everything I know.'))
    simple_command(_('hello'), _('hello to you too'))
    simple_command(_('tell me a joke'),
                   _('What do you call an alligator in a vest? An investigator.'))
    simple_command(_('three laws of robotics'),
                   _("""The laws of robotics are
0: A robot may not injure a human being or, through inaction, allow a human
being to come to harm.
1: A robot must obey orders given it by human beings except where such orders
would conflict with the First Law.
2: A robot must protect its own existence as long as such protection does not
conflict with the First or Second Law."""))
    simple_command(_('where are you from'), _("A galaxy far, far, just kidding. I'm from Seattle."))
    simple_command(_('your name'), _('A machine has no name'))

    actor.add_keyword(_('time'), SpeakTime(say))
    
