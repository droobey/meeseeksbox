# meeseeksbox
Google AIY Voice Kit Project based on a Meeseeks Box

This is a modified version of Googles Raspbian scripts for the AIY Voice Kit Project to make it like a Meeseeks Box by adding sound effects.

As well as this there are a few noticeable fuctions in the action.py

* Command configuration by text file

The script will now read commands from "cmd-config" on start
```
actor.add_keyword('parrot', Voom(say,"Norwegian Blue",4000000))
```
would become
```
parrot=Voom,Norwegian Blue,4000000
  ^      ^        ^              ^
Voice    |        |              |
Command  |        |              |
       Action     |              |
       Class  Parameter   Extra Parameter
```
in the file

* Random TV Episode

Get a random episode from a TV show
Theres a section in action.py in the EpisodeRandom class to set your favourites to search from when saying 'random episode'
Or you can say 'random episode of <showname>' for any show.
Note you will need an API key from The TVDB for this to work. [Get that here](http://thetvdb.com/?tab=apiregister) and insert it into to action.py (again in the EpisodeRandom class)

* Wav Chance
Make a command play a Wav with a chance to play a different one. Chance will be 1/number of your choosing. Also if the different wav doesnt play
it -1 from the chance, making it more likely to play it next time the command is run.
Put your wavs in the *wavs/chance* folder, *sound.wav* for the normal one and *sound-full.wav* if you are lucky!

Also I did add something a little extra...
