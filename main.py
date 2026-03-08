import pygame as pg
import math
import time
from fnc import *

BG = load_ig("grass.jpg")
FINISH = pg.transform.rotate(load_ig("checkpoint.png"),90)
WIDTH, HEIGHT = (1440,900)
CENTER = (WIDTH/2.3,HEIGHT/2.3)
win = pg.display.set_mode((WIDTH,HEIGHT))
FINISH_MASK = pg.mask.from_surface(FINISH)
End,Start,Menu = False,False,True
Winner = None

GameModes = ["Race PvP (2P)","TimeScore (1P)"]
Tracks = ["TRACK 1","TRACK 2"]
options = [0,0,3]
o = 0
laps = 3
last = 0
intv = 200
laptime = 0
pg.init()

COLORS=[resize(load_ig(str(x+1)+"_car.png").convert_alpha(),1.4) for x in range(0,4)]

def write(text,color,coords,size = 32):
    win.blit(pg.font.Font('freesansbold.ttf', size).render(text,True,color).convert_alpha(),coords)

def blit_textures(list):
    for a in list:
        win.blit(*a)

class Car:
    def __init__(self,max_vel, rot_vel,laps):
        self.vel = 0
        self.ready = False
        self.max_vel = max_vel
        self.rot_vel = rot_vel
        self.rot = 0
        self.colcount = 0
        self.fincount = 0
        self.last = 0
        self.cooldown = 2
        self.laps = laps
        self.best = [0,0]
        self.lastlap = 0
        self.lap = 1
        self.color = 0
        self.img = COLORS[0]
        self.x, self.y = self.Start_POS
        self.check=[(*self.Start_POS,self.rot),(*self.Start_POS,self.rot),(*self.Start_POS,self.rot)]

    def collision(self, mask, x=0,y=0):
        car_mask=pg.mask.from_surface(self.img)
        car_mask = car_mask.scale((20,30))
        offset=(int(self.x-x),int(self.y-y))
        coll = mask.overlap(car_mask,offset)
        return coll
    
    def bum(self):
        self.vel = -0.7*self.vel

    def appear(self,win):
        rotate(win,self.img,(self.x,self.y),self.rot)

    def steering(self,l=False,r=False):
        if l:
            self.rot += self.rot_vel*(-0.65*(self.vel/self.max_vel)**2+(self.vel/self.max_vel))
        elif r:
            self.rot -= self.rot_vel*(-0.65*(self.vel/self.max_vel)**2+(self.vel/self.max_vel))

    def move(self):
        rad = math.radians(self.rot)
        vert = math.cos(rad) * self.vel
        hor = math.sin(rad) * self.vel

        self.x -= hor
        self.y -= vert

    def accel(self,forw=False,rev=False):
        if forw:
            self.vel=min(self.vel+0.1,self.max_vel)
        elif  rev:
            if self.vel>0:
                self.vel-=0.1
            elif self.vel<=0:
                self.vel=max(self.vel-0.08,self.max_vel*-0.60)
        else:
            if self.vel<0:
                self.vel+=0.05
            elif self.vel>0:
                self.vel-=0.05
        self.vel=round(self.vel,2)

    def addlap(self):
        if self.cooldown>20:
            if self.laps == 0:
                global counter,playtime,laptime 
                if self.lastlap == 0:
                    self.ui[1] = (counter,(255,255,255))
                    self.best[1] = counter
                    self.best[0] = playtime
                elif self.lastlap < playtime:
                    self.ui[1] = (counter,(255,100,100))
                elif self.lastlap > playtime:
                    self.ui[1] = (counter,(100,255,100))
                self.lastlap = playtime
                if self.best[0] > playtime:
                    self.best[1] = counter
                    self.best[0] = playtime
                laptime+=playtime
                self.cooldown=0
            else:
                self.lap+=1
                self.cooldown=0
        self.check=[(*self.Start_POS,self.rot),(*self.Start_POS,self.rot),(*self.Start_POS,self.rot)]
        
class Player(Car):
    def checkpoint(self):
        self.check[SEC%3] = self.x,self.y,self.rot

    def blit_ui(self):
        if self.laps != 0:
            self.ui[1]=self.lap
            write(self.ui[0],(255,255,255),self.uicords)
            write((str(self.ui[1])+"/"+str(self.laps)+" lap"),(255,255,255),(self.uicords[0]+10,self.uicords[1]+30))
        else:
            write("Best time:",(255,255,255),(1250,775))
            if self.best[1]:
                write(self.best[1],(255,255,255),(1260,805))
            self.ui[0] = "Last time:"
            write(self.ui[0],(255,255,255),self.uicords)
            if self.ui[1] != 0:
                write(*self.ui[1],(self.uicords[0]+10,self.uicords[1]+30))
    def moveset(self):
        pressed = pg.key.get_pressed()
        keys = self.keyset
        self.accel()
        self.move()
        if pressed[keys[2]]:
            self.steering(l=True)
        if pressed[keys[3]]:
            self.steering(r=True)
        if pressed[keys[0]]:
            self.accel(forw=True)
        elif pressed[keys[1]]:
            self.accel(rev=True)

    def choose(self):
        pressed = pg.key.get_pressed()
        keys = self.keyset
        if self.ready==False:
            global intv
            a=pg.time.get_ticks()>self.last+intv
            win.blit(resize(pg.transform.rotate(load_ig("arrow.png"),180),1.6),(self.x-8,self.y+25))
            win.blit(resize(load_ig("arrow.png"),1.6),(self.x+29,self.y+25))
            try:
                self.img=COLORS[self.color]
            except Exception:
                self.color=0
                self.color%=len(COLORS)
            if pressed[keys[3]] and a:
                self.color+=1
                self.color%=len(COLORS)
                self.last = pg.time.get_ticks()
            elif pressed[keys[2]] and a:
                self.color-=1
                self.color%=len(COLORS)
                self.last = pg.time.get_ticks()
            if pressed[keys[0]] and a:
                self.ready=True
                COLORS.remove(self.img)
                self.last = pg.time.get_ticks()
        if self.ready:
            win.blit(load_ig("ready.png"),(self.x-4,self.y-20))
            if pressed[keys[1]]:
                self.ready=False
                COLORS.append(self.img)
                self.color=-1
        return self.ready

    def actions(self):
        self.blit_ui()
        if self.cooldown<20:
            self.cooldown+=0.05
        if SEC%3==0:
            self.colcount = 0
            self.fincount = 0
        if self.collision(BORDER_MASK,-6,-14):
            self.bum()
            self.colcount+=1
            if self.colcount>2:
                if (int(self.x),int(self.y)) == (int(self.check[((SEC%3)+1)%3][0]),int(self.check[((SEC%3)+1)%3][1])):
                    self.x,self.y=self.Start_POS
                    self.rot = 0
                    self.vel = 0
                else:
                    self.colcount=0
                    self.x,self.y,self.rot = self.check[((SEC%3)+1)%3]

        finish_collision = self.collision(FINISH_MASK, 300,350)
        if finish_collision:
            if finish_collision[1]==0:
                self.y-=self.max_vel
                self.fincount+=1
                if self.fincount>self.laps:
                    self.x,self.y=self.Start_POS
                    self.rot = 0
                    self.vel = 0
            else:
                self.addlap()
        if self.laps!=0:        
            if self.lap>self.laps:
                global Winner,End
                Winner = self.ui[0]+" WON!"
                End = True
        self.checkpoint()
        self.moveset()

class Player1(Player):
    Start_POS = (335,300)
    keyset = [pg.K_w,pg.K_s,pg.K_a,pg.K_d]
    uicords=(70,775)
    ui=["Player 1",0]

class Player2(Player):
    Start_POS = (385,300)
    keyset = [pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT]
    uicords=(1250,775)
    ui=["Player 2",0]

clock = pg.time.Clock()
running = True
while running:
    pressed = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running=False
            break
    
    if Menu:
        a=pg.time.get_ticks()>last+intv
        if pressed[pg.K_e]:
            Menu = False
            last = 0
            TRACK = load_ig("track"+str(options[0]+1)+".png")
            BORDER = load_ig("bumps"+str(options[0]+1)+".png")
            BORDER_MASK = pg.mask.from_surface(BORDER)
            finishcords = (280-options[0]*10,350)
            textures = [(BG.convert(),(0,0)),
                        (TRACK.convert_alpha(),(0,0)),
                        (FINISH.convert(),finishcords),
                        (BORDER.convert_alpha(),(0,0))]
            if options[0]==0:
                FINISH_MASK = FINISH_MASK.scale((170,23))
            if options[1]==0:
                Players = [Player1(6.5,7,options[2]),Player2(6.5,7,options[2])]
            elif options[1]==1:
                Players = [Player1(6.5,7,0)]
            
        win.fill("black")
        write("Menu",(180,25,200),(CENTER[0]-24,CENTER[1]-150),45)
        write(Tracks[options[0]],(255,255,255),(CENTER[0]-25,CENTER[1]-50))
        write(GameModes[options[1]],(255,255,255),(CENTER[0]-70,CENTER[1]))
        if options[1]==0:
            x=10
            el = 3
            write(str("Laps: "+str(options[2])),(255,255,255),(CENTER[0]-20,CENTER[1]+50))
        else:
            x=0
            el = 2
        write("Press E to start!",(255,100,100),(CENTER[0]-80,CENTER[1]+90+x))
        if o == 0:
            write(Tracks[options[0]],(255,255,100),(CENTER[0]-25,CENTER[1]-50))
            
        if o == 1:
            write(GameModes[options[1]],(255,255,100),(CENTER[0]-70,CENTER[1]))
        if o == 2:
            write(str("Laps: "+str(options[2])),(255,255,100),(CENTER[0]-20,CENTER[1]+50))
        if pressed[pg.K_w] and a or pressed[pg.K_UP] and a:
            o-=1
            last = pg.time.get_ticks()
        if pressed[pg.K_s] and a or pressed[pg.K_DOWN] and a:
            o+=1
            last = pg.time.get_ticks()
        o%=el
        if pressed[pg.K_d] and a or pressed[pg.K_RIGHT] and a:
            options[o]+=1
            last = pg.time.get_ticks()
        if pressed[pg.K_a] and a or pressed[pg.K_LEFT] and a:
            options[o]-=1
            last = pg.time.get_ticks()
        if options[2]<1:
            options[2]+=1
        if o!=2:
            options[o]%=2
        
    else:
        blit_textures(textures)
        for car in Players:
            car.appear(win)
        SEC = list(time.gmtime())[5]
        if Start == False:
            p=[x.choose() for x in Players]
            if all(x for x in p):
                [COLORS.append(x.img) for x in Players]

                x=pg.time.get_ticks()
                while True:
                    blit_textures(textures)
                    for car in Players:
                        car.appear(win)
                    secs = (pg.time.get_ticks()-x)/1000
                    if secs<1:
                        win.blit(load_ig("3.png").convert_alpha(),(CENTER))
                    if secs>1 and secs<2:
                        win.blit(load_ig("2.png").convert_alpha(),(CENTER))
                    if secs>2 and secs<3:
                        win.blit(load_ig("1.png").convert_alpha(),(CENTER))
                    if secs>3:
                        Start=True
                        start_ticks = pg.time.get_ticks()
                        break
                    pg.display.flip()
        
        elif Start==True and End == False:
            playtime = pg.time.get_ticks()-start_ticks-laptime
            m = str(playtime//60000).zfill(2)
            s = str((playtime%60000)//1000).zfill(2)
            ms = str((playtime%1000)//10).zfill(2)
            counter = "%s:%s:%s" % (m,s,ms)
            write(m+".",(255,255,255),(0,0),35)
            write(s+".",(255,255,255),(49,4),30)
            write(ms,(255,255,255),(92,9),23)
            for car in Players:
                car.actions()
            
        else:
            write(Winner,(255,255,255),CENTER)
            write(counter,(255,255,255),(CENTER[0]+50,CENTER[1]+50))

    if pressed[pg.K_ESCAPE] and Menu==False:
        End,Start,Menu = False,False,True
        Winner = None
        options = [0,0,3]
        o = 0
        laps = 3
        last = 0
        intv = 200
        laptime = 0
        Player1.ui = ["Player 1",0]
    pg.display.flip()
    clock.tick(60)
pg.quit()