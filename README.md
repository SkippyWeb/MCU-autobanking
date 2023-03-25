# MCU hack (Autobanking)



![](https://github.com/SkippyWeb/Images/blob/main/SkippyStudio.jpg)



For discussion see: https://forums.steinberg.net/t/mackie-controller-auto-banking/159549/52



**Content**

**simplifiedhackiemackie.py** 

* to implement track follow for MCU controllers

* Provided by Shor
* Developed in Python 2

* Copied from: https://github.com/krixgris/simplifiedhackiemackie



**Hackie_Mackie_base.py** 

* provided by MC89
* Improved version? (I did not check)
* Copied from https://app.box.com/s/uob2rfpqnfz7qiyeae7h1ytciyxq6d5f



**mcupython**

* Provided by Shor
* Developed in Python 3
* Improvement of **simplifiedhackiemackie.py**
* The main program is hackiemackie.py
* Configuration can be done in the midiconfig.py
* Copied from https://github.com/krixgris/mcupython





**License**

All of the applications provided in these repository are free but I am not the owner. See the source websites for more further, details, license information, or newer versions.



**Information from the Cubase forum**

<u>Message</u>

I can see it being desirable to have your faders and tracks stay where they are, but at least you should have the option like mentioned.
For me, I use a Behringer X-Touch One controller, which is a single fader + track controls + transport… so for that usecase you (well me anyway) always want it to follow the selected track.
I use a Console 1 with the Fader next to this, so having track selections follow my Console 1 is really really awesome. Before I was constantly forced to manually bank if I wanted to get any use from my X-Touch… I also do use the display on it to see which track I have selected, as my setup is often run without me necessarily looking on my screen.

Interesting fact:
Cubase Pro 11 does this differently than Cubase Elements 10 (and presumably 10 Pro).
I just tried these two as I have both installed… but in Elements the sysex with the track names also comes with the track number of the first track in the bank, so essentially that gives you a track number, making navigating easier.

However in Cubase 11 Pro you don’t get that.

I can use names if I let my program browse through all the banks and map it out, but I haven’t done that, as that also means it is unreliable if I change names etc… I have been considering adding this as an extra method to help me find banks faster though.

The way I find them is unfortunately brute forcing them, as I haven’t found any good clues to help me navigate (other than using the names and learning which tracks are where).
What happens when Cubase selects a track that isn’t the selected bank in Mackie Controller is that it sends a note off on all tracks, and that lets me know it’s not the right track.
So I go up x times, and then down x times. If I find the bank, one of the tracks will get a note on, and then i stop.
If I can’t find it, I stop after a set of attempts. This is actually quite quick, and I can optimize it more…but right now it works really really well for me, and it does the trick.
When you select midi tracks, or folders it will cause a wrong bank to be selected, and my logic fires as well, but that’s fine. Doesn’t cause any problems whatsoever. The next time Cubase selects a valid track, it’ll fire again, and find it.

Oh and lastly, how I’m actually able to control the messages like this is by just creating a virtual midi track that I use as a mackie controller.
Then in my program I communicate between the virtual device and my actual hardware controller to make this play nicely.   



<u>Message</u>

Important things to note is that this assumes you have a way to set up virtual midi ports.
Things to hack in the script involve midi port names, and potentially the value for number of max jumps to attempt auto-banking. It can’t be infinite, or you’ll be stuck in an infinite loop in the cases where there is no valid bank (such as master track, midi tracks, folder tracks etc).

Also, if you want it to work faster, you can adjust the sleep timer variable to a lower value, but this will come at a cpu cost.

Again, this is very very very proof of concept stuff and inefficient. But it proves the concept can work very well.

Again this is so beta, and will require some small work potentially to get going, but I do have this running myself on MacOS and Cubase 11 Pro with an X-Touch One and it works quite well.

​    

<u>Message</u>

Where I think you may be tripping up is here:

1. These should not be a part of all midi in Cubase, just to make sure it’s not doing dumb things where it shouldn’t be
2. The virtual device (or the one actually being used for mackie) is confusingly named. For the midi in port, I set it up to use the midi OUT, and for midi out i use midi IN.
   This is a bit confusing, but basically since it listens to cubase, and sends it out to the real x-touch etc…
3. In Cubase, you set up the virtual/piggybacked device as your mackie controller, not the physical X-Touch.
   All communication to and from the X-Touch is done via the script
   In Cubase, as I did make it unnecessarily confusing in step 2, I have midi out set to be the midi in on the virtual device, and midi in to be midi out. Feel free renaming this as needed
4. There’s a variable right now that I can’t recall that sets how many max steps to try to auto-bank before it stops, so keep that in mind as well
5. If you have some latency, you can change the sleep timer variable as well
6. Sorry, Python 2 is what I used to build this. All python things I build from now on will likely be in python 3 though, but yeah… 2 is what I used so there may be issues there.



<u>Message</u>

Doesn’t seem to lose device reference upon restarting Cubase and disconnecting/reconnecting the X-Touch (which has my MIDI keyboards plugged into it). I’m using loopMIDI for the virtual driver btw.

The script is for sure a game-changer for the X-Touch (and other Mackie controllers too I presume?) Funny how someone with some Python know-how can do something Steinberg couldn’t in 11 versions.

Ah, loopMIDI is probably what saves you from not losing the device. That’s great.



<u>Message</u>

OK, I’m posting a quick guide on how to set up the script to run on Windows. It will run on Mac as well, the biggest difference being that Mac users don’t need a third-party app in order to get virtual MIDI ports as they can just use the IAC Driver for that.

The script is set up for the X-Touch One but it should also work on other single fader controllers if you rename a couple of lines in the code. I will mention how to do so below.

1. We need to set up virtual MIDI ports. I used loopMIDI but you can use another application if you like.
   [loopMIDI | Tobias Erichsen 15](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Launch loopMIDI, delete the port it creates for you, and create two new ports, name them loopMIDI Port IN, and loopMIDI Port OUT. If you’re not using loopMIDI it would be easier if you still used these port names as they are coded into the script.
3. Install Python from the Microsoft Store (don’t get the one from the Python website as that could complicate some things). This version of the script works on Python 3.
4. Open a Command Prompt (by typing cmd in the taskbar) and type `pip install mido`
5. Next type `pip install python-rtmidi`
6. Download the script: [Dropbox - Hackie_Mackie_base.py - Simplify your life 32](https://www.dropbox.com/s/l0r6mdcqnaui2mx/Hackie_Mackie_base.py?dl=0)

6b. This step is only for those not using an X-Touch One. Open the script with something like Notepad. You’ll notice ‘X-Touch One’ written twice near the top. In your DAW, look at the MIDI Ports for the exact name of your controller (in Cubase this is in Studio Setup → MIDI Port Setup) and use that name to replace both instances of ‘X-Touch One’ in the script. Save and close.

1. Run the script by double-clicking it. It’ll run as long as the window stays open.
2. In Cubase open Studio Setup and under MIDI Port Setup untick everything next to loopMIDI and your Mackie controller. If you’re not using Cubase do the same in whichever DAW you’re using.
3. In Mackie Control - for the MIDI Input choose loopMIDI Port OUT, and for the MIDI Output choose loopMIDI Port IN. I did not mistype that, the ports need to be reversed like that.

Alright, if everything was done correctly you should now hopefully have full auto-banking. As mentioned in an earlier post, if you use a large amount of tracks, find this line in the script ‘if(7> bankCounter >=0):’ and increase the value from 7 to the number of banks you’d like to use. Also, in ‘if(bankCounter >= 15):’ increase the value for the maximum amount of jumps to the number of banks you chose times 2. You can also adjust the sleeptimer to a lower value to make it work faster, at a CPU cost.

​    

<u>Message</u>

I got inspired to go back in with coding, now that i was having some issues with the current script using the Mac OS IAC midi devices, as they apparently have some new behaviour since Big Sur or Monterey.

New version of this is on the way now. I am re-writing the midi loop now in a way where it should have significantly better performance, and no need for a sleep timer (probably, but initial tests seem to indicate there’s no need anymore now).
I migrated the script to work in python 3 now.
It’s still under construction, but I am refining the logic, and right now I am keeping track of which direction to bank if you use track selectors on the mackie controller, and I’m considering options for figuring out a faster algorithm for auto-banking, which really shouldn’t be too bad.
Ideally I want to omit the need to work with a max number of skips to attempt, and have it automatically work it out.

At this point I should add that I am mainly targeting a single fader controller (I am using the Behringer X-Touch One), and as I don’t have a mackie controller with 8 faders, I don’t have any way to test how the following things will behave on those.
A thing I’m working on is setting a nicer track name on the display, as well as opening up for using 2 rows of the LCD to display longer names.
This thread opened up for some ideas regarding this: [Creative thinking needed (?), retrieve track names from Cubase to MIDI or OSC - #22 by Shor 7](https://forums.steinberg.net/t/creative-thinking-needed-retrieve-track-names-from-cubase-to-midi-or-osc/717977/22)

Basically making use of the MCU commands to go into eq, channel strip, aux send modes you will get a longer track name, so I am thinking about making use of this to read out track names. It’s a bit tricky to figure out how to do this in the best way.
I already made some functions for conveniently setting names making use of both rows, but I need to work out how to override the original mackie behaviour in a way where it all works without glitches.
Rough idea right now is to figure out if a track change is performed, and then switch modes to get a long name, and then switch back to the ‘normal’ mode again.

The names will come after working out a better way to autobank, and I am hopefully going to be done with that this coming week.
Unfortunately this is really an ‘as is’ solution, but I’m thinking this version will be significantly easier to work with and setup. I’m hoping there wont be more configuration than naming your midi devices.

   

<u>Message</u>

I keep following this thread and your new inventions, because it’s really cool and extremely useful. And yes, you are a great fellow, many like me use your script - it’s excellent. Just a week ago, I came across the fact that the script really stopped working on Windows 11 (possibly after the next last update), but it simply stopped opening. We will wait for your new (updated) script, perhaps it will also work already on the new Windows 11.



I’m curious, what actually stopped working?
Maybe python 2 problems since it is now deprecated…

Anyway, I’ve been struggling to make time on my end, but trying to get a few minutes of coding and testing in on the mornings now on the next version of this, and it’ll happen.
For anyone interested in potentially trying it when it’s “done enough” I can infor that you’ll likely need to update to python 3.10 or later, and it’ll still need mido as well as rtmidi modules to run.

I can’t really say any estimate on when I’ll be done, as my coding time is very limited. The auto-banking logic is a bit tricky, so I’ve been working on making it a bit more abstract so it’ll be less keeping track of numbers and weird sysex (hopefully).

On the old one I locked away banking from the controller, but I am considering allowing for that now, but maybe with an option. The problem there is that changing banks manually would trigger it to start searching for the bank with a track in it, so to override that I’m thinking that banking to previous bank might just default to selecting the last track in the bank, and banking to next bank could select the first track in the bank.
Similar logic is already implemented now when track switching. If you track switch to the next track and you are currently on the last track, it automatically sends a next bank, and selects the first track in the bank. - Prev track when on the first track in a bank will send prev bank, and select the last track in the bank.
Makes sense to me at least.
I also added a debug mode now, mainly for development use, which lets you use one more (or many more) midi devices to also send mackie commands. I’ll leave that in probably, as that means that you can, if you want to, map mackie controls to any other midi device if you want. Not sure if there’s any real use for this, but I used it now on my keystep just so I can send mackie controls that my single fader control doesn’t have. Such as changing to EQ mode, Insert mode etc… not actually sure how useful that is on a single fader controller yet, but it was neat seeing my plugins on the LCD. I do intend to figure out some way to use this to get a longer track name though, and then using that to set a nicer name on my controller. This might have to be an option you can use or not use though, as I suspect these hacks might make user experience annoying on an 8 fader controller.



<u>Message</u>

I don’t want to jump the gun on this, seeing as my time to spend programming this new version of the auto-banking has been more limited than I had anticipated, but I think I might be close to have an initial version of a reworked script for this.

I have coded a smarter logic for figuring out how to bank, and determining when we are in the correct bank.
No more sleep timer config, no more max jump settings. I have a way to traverse through all banks now until track is found, and if a non valid track (such as group track, chord track, midi track) is selected, it’ll scan up and down the bank list once, and then no more until another track is selected.

Right now I am cleaning up code, and need to refactor some parts to make it neater, but it looks like I have about 3-4h tonight for some coding work, so I am hoping I have a test ready version.

Does anyone want to give a hand in trying a new version of this when the intial version is done?
I run this on Mac OS Monterrey and current version uses Python 3.10. Some earlier version of Python 3 might work, but I can’t guarantee it.
I don’t have a way to try this in windows really… possibly I could see if it just runs in Win 10, but no way to test Win 11.
To run it, you might need to have a little bit of know how to at least install python and modules, as well as potentially needing to know how to set up a virtual midi device.
Setup needed by a user just setting up which midi ports DAW uses, as well as which midi ports your hardware uses. Running the program once without doing a config will prompt an error, but will also list available ports on your system, so that’s what you’d need to edit in one of the files (the file is just called midiconfig.py and should be straight forward).
Ideally I want to make this a bit more beginner friendly to use, but at least this feels way way simpler to set up than the initial version.





<u>Message</u>

Oh awesome.
Unfortunately I am really novice for setting this up in windows, as I mainly use Mac.

Step by step guide from the previous version should work mostly I’d imagine (maybe someone can chime in here with better instructions).
The actual steps required will be:

- Download the .py files from git (I’ll provide a link once I’m done).
- Install Python 3.10 (anything later should work as well of course)
- Install the following modules: mido (this is the midi module i used last time), python-rtmidi (this is the midi port, also used the last time).
- Opening the file called midiconfig.py with an editor (notepad or whatnot) and editing some clear text parameters. DAWOUTPUT ,DAWINPUT, HWOUTPUT,HWINPUT

There are additional parameters in there now as well, one being DEBUG which is 0 or 1, and with enabled will spit out a lot of messages in the console, mostly used for development. If DEBUG is enabled, you also need to config the DEBUGDEVICE. If DEBUG is 0, you can just ignore it.
Another is AUTOBANK which well, is the whole point…and I just wanted to have a parameter to switch it on or off, for whatever reason.

After that it’s just a matter of starting the program.
Syntax should just be something like “python3.10 hackiemackie.py” in the same folder that the other files are.

Anyway, I’ll try to get some progress tonight and hopefully have some actual files posted.



<u>Message</u>

Ok first release in… it’s a bit messy, so a lot of cleanup is still needed, and i definitely need to update documentation, but I got first version working now.


Things that aren’t working as well as I’d like is that I still don’t know which direction to start searching for banks, so right now I start going up, and then it turns around and searches to the bottom. If it doesn’t find a track, it wont try again until you select a new track.
I am hoping to be able to improve this logic, but it’s really tricky to work out… it can be done, but requires a few hacky things, which I don’t shy away from, but yeah…wanted a working version first, which I consider this to be.

The main program is hackiemackie.py
Configuration can be done in the midiconfig.py

Available for download below, there’s a source code zip you can download from there.

   

<u>Message</u>

I’d say try to install using pip3 install python-rtmidi instead?
pip might be python 2.
I do recognize this ‘wheel’ package not installed error, but can’t recall what the issue is regarding that.
Try typing pip list and you should see a list of modules installed. Quite possibly you might have to type pip3 list as well.
Personally I run the latest binary (executable files) for python, so when I installed these modules i did pip3.10 install python-rtmidi and then pip3.10 install mido.
If I run that I get the following result:
