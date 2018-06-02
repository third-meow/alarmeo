#!/usr/bin/env python3

import os
import time
import subprocess
import RPi.GPIO as GPIO
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class alarm():
    def __init__(self):
        #initiate all the things
        self.recog = aiy.cloudspeech.get_recognizer()
        self.recog.expect_phrase("I'm lazy")
        self.recog.expect_phrase('I will get up')
        
        self.button_pin = 23
        GPIO.setup(self.button_pin, GPIO.IN)
        
        self.led = aiy.voicehat.get_led()
        aiy.audio.get_recorder().start()

        
        #list of music to play
        self.tracks = [
                '/home/pi/beats/qq.wav',
                '/home/pi/beats/kmn.wav'
                ]

        #for keeping track of current track and volume
        self.track_num = 0
        self.current_vol = 0
        
        
        print('*' * 150)

        #ask user for alarm time
        self.target_hour = self.og_target_hour = int(input('Hour: '))
        self.target_min = self.og_target_min = int(input('Min: ')) - 1



    #return the track path found in self.tracks.
    def get_track_path(self):
        #if self.track_num is higher than length of self.tracks, cycle back to start
        return self.tracks[self.track_num % len(self.tracks)]



    def get_now(self):
        the_time = time.localtime()
        self.now_hour = the_time.tm_hour
        self.now_min = the_time.tm_min



    def off(self):
        #turn led off
        self.led.set_state(aiy.voicehat.LED.OFF)

        #reset alarm time, track number and volume
        self.target_hour = self.og_target_hour 
        self.target_min = self.og_target_min
        self.track_num = 0
        self.current_vol = 0



    def snooze(self):
        #set led to blink
        self.led.set_state(aiy.voicehat.LED.BLINK)

        #increase track number
        self.track_num += 1

        #set target time to 6 minutes from now
        self.get_now()
        self.target_hour = self.now_hour
        self.target_min = self.now_min + 6

        while self.target_min > 59:
            self.target_hour += 1
            self.target_min -= 60
        
        #wait 5 seconds
        time.sleep(5)

        #turn led off
        self.led.set_state(aiy.voicehat.LED.OFF)



    #cut the beats and take message
    def take_msg(self):
        #turn led off
        self.led.set_state(aiy.voicehat.LED.OFF)

        #wait two seconds
        time.sleep(2)

        #stop beats and set LED to on
        self.playqq.kill()
        self.led.set_state(aiy.voicehat.LED.ON)

        #take input from user
        self.text = self.recog.recognize()
        
        #turn led off
        self.led.set_state(aiy.voicehat.LED.OFF)



        #depending on input snooze, turn off or sound alarm again
        print(self.text)

        if self.text != None:
            if 'I will get up' in self.text or "I'll get up" in self.text:
                self.off()
            elif "I'm lazy" in self.text:
                self.snooze()
            else:
                print("Can't find message in text")
                self.sound_alarm()
        else:
            print("Can't find message in text")
            self.sound_alarm()




    #sound the alarm
    def sound_alarm(self):
        #turn LED to blink
        self.led.set_state(aiy.voicehat.LED.BLINK)

        print(self.target_hour)
        print(self.target_min)

        DEVNULL = open(os.devnull, 'w')

        #set initial volume to zero
        subprocess.Popen(['amixer', 'sset', 'Master', '0%'], stdout=DEVNULL)
        
        #use aplay to play the beats
        self.playqq = subprocess.Popen(['aplay', self.get_track_path()])
        
        #slowly increase the volume to 90 percent
        for i in range(0, 10000):
            #wait 30 milli-secs
            time.sleep(0.030)
            
            #if button is pushed, break from loop
            if GPIO.input(self.button_pin) == False: 
                break
            
            #increase volume
            if (i % 500 == 0) and (self.current_vol <= 85):
                self.current_vol = i / 100
                subprocess.Popen(['amixer', 'sset', 'Master', str(self.current_vol)+'%'], stdout=DEVNULL)
        
        #take message
        self.take_msg()



    def main(self):
        while True:
            #keep LED off
            self.led.set_state(aiy.voicehat.LED.OFF)
       
            #get time
            self.get_now()
       
           #if time is user set alarm time, sound alarm
            if self.now_hour ==  self.target_hour and self.now_min == self.target_min:
                print(time.localtime())
                self.sound_alarm()

            #wait 30 secs
            time.sleep(30)


if __name__ == '__main__':
    a = alarm()
    a.main()







