#!/usr/bin/env python3

import time
import subprocess
import RPi.GPIO as GPIO
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

GPIO.setmode(GPIO.BCM)

class alarm():
    def __init__(self):
        #initiate all the things
        self.recog = aiy.cloudspeech.get_recognizer()
        self.recog.expect_phrase('i am lazy')
        self.recog.expect_phrase('i am not lazy')
        self.recog.expect_phrase('yes')
        
        self.button_pin = 23
        GPIO.setup(self.button_pin, GPIO.IN)
        
        self.led = aiy.voicehat.get_led()
    
        self.tracks = [
                '/home/pi/beats/qq.wav'
                ]

        self.track_num = 0
        self.current_vol = 0
        
        #ask user for alarm time
        self.target_hour = self.og_target_hour = int(input('Hour: '))
        self.target_min = self.og_target_min = int(input('Min: ')) - 1


    def get_track_path(self):
        #return the track path found in self.tracks.
        #if self.track_num is higher than length of self.tracks, cycle back to start
        return self.tracks[self.track_num % len(self.tracks)]

    def off(self):
        self.target_hour = self.og_target_hour
        self.target_min = self.og_target_hour
        self.track_num = 0
        self.current_vol = 0

    def snooze(self):
        self.track_num += 1
        self.target_min += 6

        while self.target_min > 59:
            self.target_hour += 1
            self.traget_min -= 60



    #turn down beats and take message
    def take_msg(self):
        #aiy.audio.get_recorder().start()
        #time.sleep(1)
        self.playqq.kill()
        #self.text = self.recog.recognize()
        
        self.off()

        #if 'i am lazy' in self.text:
        #    self.snooze()
        #elif 'i am not lazy' in self.text:
        #    self.off()
        #else:
        #    self.sound_alarm()

    #sound the alarm
    def sound_alarm(self):
        #set initial volume to three percent
        subprocess.Popen(['amixer', 'sset', 'Master', '3%'])
        
        #use aplay to play the beats
        self.playqq = subprocess.Popen(['aplay', self.get_track_path()])
        
        #slowly increase the volume to 90 percent
        for i in range(0, 10000):

            print(i)
            #wait 30 milli-secs
            time.sleep(0.03)
            
            #if button is pushed
            if GPIO.input(self.button_pin) == False:
                self.take_msg()

            if (i % 500 == 0) and (self.current_vol <= 85):
                #increase volume
                self.current_vol = i / 100
                subprocess.Popen(['amixer', 'sset', 'Master', str(self.current_vol)+'%'])
        
        while GPIO.input(self.button_pin):
            pass
        self.take_msg()


    def main(self):
        while True:
            #cheak time
            time.sleep(30)
            the_time = time.localtime()
            now_hour = the_time.tm_hour
            now_min = the_time.tm_min
            
            #if time is user set alarm time, sound alarm
            if now_hour ==  self.target_hour and now_min == self.target_min:
                self.sound_alarm()

if __name__ == '__main__':
    a = alarm()
    a.main()







