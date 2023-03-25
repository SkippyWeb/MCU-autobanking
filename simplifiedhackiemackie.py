# coding=utf-8

import mido
from mido.ports import MultiPort
import time
import string


##
##		TODO: Fixa matrix för vald track
##			Lagra vilken bank man har valt, dvs f1, f9, f17 osv.. och använd det för att veta vilket håll man ska banka
###
##		Virtual ports communicate with the DAW and is set up as the midi in/out
##		Virtual ports listen to the output of the actual hw controller, and sends the hw output to the mackie controller input
##		Virtual port input receives midi from cubase, and sends it to the controller
##
##		Additional messages are sent to the virtual port to compensate for banking, track selection
##
##
##		A matrix/dictionary of the 8 tracks and their selection status + names is stored 

midiOutput = 'X-Touch One'
midiInput = 'X-Touch One'
### note that the virtual ports are a bit backwards, input is an output, and output is an input
### due to DAW speaks to the input of the virtual device, and that outputs to the input of the harware device

### mido can handle virtual ports, but making IAC ports in macos will keep these ports static, and daws like cubase wont forget them
midiInputVirtual = 'IAC Driver HackieMackie OUT'
midiOutputVirtual = 'IAC Driver HackieMackie IN'

#midiInputVirtual = 'AIAC Driver HackieMackie'
#midiOutputVirtual = 'AIAC Driver HackieMackie'


sleeptimer = 0.025
bankSwitchStart = float()
bankSwitchDelta = float()


if(midiInput not in mido.get_input_names()):
	print 'Input port not found, check settings and try again. See available ports below:'
	print mido.get_input_names()
	quit()
if(midiOutput not in mido.get_output_names()):
	print 'Output port not found, check settings and try again. See available ports below:'
	print mido.get_output_names()
	quit()

outport = mido.open_output(midiOutput)
outportVirt = mido.open_output(midiOutputVirtual)

mackieTracksVirt = {24:0, 25:0, 26:0, 27:0, 28:0, 29:0, 30:0, 31:0}
mackieTracks = {24:0, 25:0, 26:0, 27:0, 28:0, 29:0, 30:0, 31:0}
mackieTrackNames = {24:'', 25:'', 26:'', 27:'', 28:'', 29:'', 30:'', 31:''}
mackieTracksReset = {24:0, 25:0, 26:0, 27:0, 28:0, 29:0, 30:0, 31:0}

mackieTrackChange = 0
currentBank = 1
prevBank = 9
actualBank = 1

bankCounter = 0
autoBankFail = False

def UpdateTrackNames (BankNameList):
	global currentBank
	global prevBank
	all=string.maketrans('','')
	nodigits=all.translate(all, string.digits)

	global mackieTrackNames
	b = BankNameList.split(' ')
	mackieTrackNames = {24:b[0], 25:b[1], 26:b[2], 27:b[3], 28:b[4], 29:b[5], 30:b[6], 31:b[7]}
	print b
	print b[0]
	prevBank = currentBank
	currentBank = int(b[0].translate(all, nodigits))
	print currentBank
	print mackieTrackNames

bankChangePending = True

# keyboard.wait('f')
# print 'ok'


with mido.open_input(midiInput) as port:
	with mido.open_input(midiInputVirtual) as virtPort:
		while(True):
			MessageBatch = list()
			MessageBatchVirt = list()
			for msg in virtPort.iter_pending():
				MessageBatchVirt.append(msg)
				if (msg.type == 'sysex' and len(msg.data))>50 and 1==2:
					print 'sysex with useful stuff'
					#evalute length of sysex
					# we only care about sysex carrying first track number
					# as well as names (6 char length)
					#
					#print len(msg.data)
					isInit = False
					if (len(msg.data)==62):
						print "INIT SYSEX (length:" + str(len(msg.data)) + ")"
						isInit = True
					else:
						print "UPDATED BANK (length:" + str(len(msg.data)) + ")"
					# figure out how to store the names + bank track# in our 8 track matrix
					sList = list()
					for s in str(msg.hex()).split(' '):
						if( s.isalnum() or s.isspace):
							if s != 'F0' and s != 'F7':
								sList.append(s.decode('hex'))
					#print sList
					newString = "decoded hex:"
					decodedString = ""
					for s in sList:
						if( s.isalnum() or s.isspace):
							decodedString += s
					print newString + decodedString
					if(isInit == False):
						UpdateTrackNames(decodedString)
				# elif (msg.type == 'sysex'):
				# 	print 'useless sysex'
				else:
					pass
				if((msg.type == 'note_on' or msg.type == 'note_off') and msg.note in [51,74,75] and 1==2):
					#do we need to handle any messages and not send them to our HW controller?
					pass
				else:
					outport.send(msg)

			autoBankNeeded = False
			didStuff = False
			mackieTrackList = list()
			for msg in MessageBatchVirt:
				if((msg.type == 'note_on' or msg.type == 'note_off') and msg.note in mackieTracks.keys()):
					mackieTrackList.append(msg.velocity)
					didStuff = True
				#	these seem to get sent as a 'mackie changed something with selected tracks'
				if((msg.type == 'note_on' or msg.type == 'note_off') and msg.note in [51,74,75]):
					didStuff = True
			if(didStuff or bankCounter>0):
				if(127 in mackieTrackList):
					print 'Bank correct'
					print "Auto-bank time: " + str(time.time()-bankSwitchStart) + " seconds."
					autoBankFail = False
					bankCounter = 0
				else:
					if(bankCounter == 0):
						bankSwitchStart = time.time()
					print 'Incorrect bank'
					if(7> bankCounter >=0):
						print 'Auto-banking UP'
						outportVirt.send(mido.Message('note_on', channel=0, note=47, velocity=127, time=0))
						outportVirt.send(mido.Message('note_off', channel=0, note=47, velocity=0, time=0))
					else:
						print 'Auto-banking DOWN'
						outportVirt.send(mido.Message('note_on', channel=0, note=46, velocity=127, time=0))
						outportVirt.send(mido.Message('note_off', channel=0, note=46, velocity=0, time=0))
					bankCounter +=1
					if(bankCounter >= 15):
						print "Auto-banking gives up..RIP"
						print str(time.time()) + '\n'
						autoBankFail = True
						bankCounter = 0

					
					# if(msg.velocity == 127):
					# 	noteOn = True
			

			#HW MIDI loop input. Input of HW listens to what HW SENDS, not Receives.
			# Catch any messages we send here in case we need to implement extra logic
			# Example: On track 8 ,pressing next track will select track 8 again, if track 8 is selected, we should bank UP
			#			Likewise, track 1 and pressing prev track selects track 1 again, if we get repeat, bank DOWN
			# anything we receive from HW, send to virtual outport, which gets picked up by DAW
			for msg in port.iter_pending():
				MessageBatch.append(msg)
				if((msg.type == 'note_on' or msg.type == 'note_off') and msg.note in mackieTracks.keys()):
					mackieTracks = mackieTracksReset.copy()
					if(msg.velocity>0):
						mackieTracks[msg.note] = 1
						print mackieTracks
					else:
						mackieTracks[msg.note] = 1
					actualBank = currentBank
					# print msg
				outportVirt.send(msg)
			
			time.sleep(sleeptimer)
			isInBank = 0

			# order of this logic is very important, as messages processed here will be gone in the next loop
			# bankChangePending is set before the next messages arrive at the virtual input
			###
			# so process messagebatchvirt before the non-virt
			#
			noteOn = False
			bankProcessed = False
			mackieTrackChangeVirt = False
			mackieCountTracks = 0

			# if(bankChangePending):
			# 	print "Process BANK logic"
			# 	for msg in MessageBatchVirt:
			# 		if((msg.type == 'note_on' or msg.type == 'note_off') and msg.note in mackieTracksVirt.keys() and msg.velocity == 0):
			# 			if(msg.type == 'note_on' and msg.velocity == 127):
			# 				noteOn = True
			# 			mackieCountTracks += 1
			# 			print "virt does stuff to: " + str(msg.note) + 'vel: ' + str(msg.velocity)
			# 			# mackieTrackChange = True
			# 			# mackieTracks = mackieTracksReset.copy()
			# 			# mackieTracks[msg.note] = 1
			# 			#print msg
			# 			if(noteOn == False and mackieTrackChangeVirt == False):
			# 				mackieTrackChangeVirt = True
			# 				mackieTracksVirt = mackieTracksReset.copy()
			# 		if (mackieTrackChangeVirt):
			# 			bankProcessed = True
			# 	if (bankProcessed == False):
			# 		print 'Bank update, but nothing changed, end or start of bank list?'
			# 	print 'Processed ' + str(mackieCountTracks) + ' events.'
			# 	if(mackieCountTracks == 8):
			# 		bankJumps = (actualBank-currentBank)/8
			# 		print "This is not the bank (" + str(currentBank) + ") and prev was " + str(prevBank) + " \nActual bank is: " + str(actualBank) + "\nJumps to actual is:" + str(bankJumps)
			# 		# do things for banking
			# 		# if(bankJumps>0):
			# 		# 	outport.send(mido.Message('note_on', channel=0, note=47, velocity=127, time=0))
			# 		# 	outport.send(mido.Message('note_off', channel=0, note=47, velocity=0, time=0))
			# 		# elif(bankJumps<0):
			# 		# 	outport.send(mido.Message('note_on', channel=0, note=46, velocity=127, time=0))
			# 		# 	outport.send(mido.Message('note_off', channel=0, note=46, velocity=0, time=0))
			# 	elif (mackieCountTracks == 7):
			# 		print "This IS the bank (" + str(currentBank) + ") and prev was " + str(prevBank)
			# 		actualBank = currentBank
			# 	else:
			# 		print "No events for track selection. End of bank? "
			# 	bankChangePending = False
				

			#can i do this in main loop?
			noteOn = False
			for msg in MessageBatch:
				#print msg
				if(msg.type == 'note_on' and msg.note in [46,47] and msg.velocity == 127):
					#print 'bank'
					if msg.note == 46:
						print "DOWN DOWN DOWN DOWN"
						print "=====BANKING======="
						print "DOWN DOWN DOWN DOWN"
						#bankChangePending = True
						#print mackieTracks
					if msg.note == 47:
						print "UP UP UP UP UP UP  "
						print "=====BANKING======="
						print "UP UP UP UP UP UP  "
						bankChangePending = True
						#print mackieTracks
				#outportVirt.send(mido.Message('note_off', channel=0, note=24, velocity=0, time=0))
				#outportVirt.send(mido.Message('note_on', channel=0, note=47, velocity=127, time=0))

			mackieTrackChange = False

