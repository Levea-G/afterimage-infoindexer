import sqlite3 as sql
from typing import Union
import pygame
from os import environ
from io import BytesIO
unitwidth:int=300
class frame:
    def __init__(self,pos:tuple)->None:
        self.x,self.y=pos[0],pos[1]
        self.frame:pygame.Surface=None
        self.xscroll=self.yscroll=0
        self.elements:list[list[pygame.Surface]]=[]
        self.xsum=self.ysum=0
        self.indx=[]
    def inside(self,pos:tuple)->bool:
        return self.x<=pos[0]<=self.x+800 and self.y<=pos[1]<=self.y+self.ysum
    def DealEvent(self,event:pygame.event.Event)->None:
        if event.type==pygame.MOUSEBUTTONDOWN:
            if not self.inside(event.pos):return
            if event.button==5:self.yscroll=min(max(0,self.ysum-665),self.yscroll+30)
            elif event.button==4:self.yscroll=max(0,self.yscroll-30)
        elif event.type==pygame.MOUSEMOTION:
            if event.pos[0]>900:self.xscroll=min(max(0,self.xsum-800),self.xscroll+10)
            elif event.pos[0]<100:self.xscroll=max(0,self.xscroll-10)
    def draw(self,root:pygame.Surface)->None:
        for i,line in enumerate(self.elements):
            tempx=0
            for _,indv in enumerate(line):
                self.frame.blit(indv,(tempx,i*unitwidth))
                if indv.get_width()>200:tempx+=unitwidth
                else:tempx+=150
        root.blit(self.frame,(self.x-self.xscroll,self.y-self.yscroll))
class entry:
    def __init__(self,size:tuple,pos:tuple,boxcolor:Union[tuple,str],focuscolor:Union[tuple,str],textcolor:Union[tuple,str],font:pygame.font.Font,initcontent:str='')->None:
        self.focused:bool=0
        self.width,self.height,self.size=size[0],size[1],size
        self.x,self.y,self.pos=pos[0],pos[1],pos
        self.basicfont=font
        self.text=initcontent
        self.textface=font.render(initcontent,True,textcolor)
        self.bcolor=boxcolor
        self.fcolor=focuscolor
        self.tcolor=textcolor
        self.toleft=0
    def inside(self,pos:tuple)->bool:
        return self.x<=pos[0]<=self.x+self.width and self.y<=pos[1]<=self.y+self.height
    def DealEvent(self,event:pygame.event.Event)->None:
        if event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==4 or event.button==5:return
            self.focused=self.inside(event.pos)
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_BACKSPACE:
                self.text=self.text[:-1]
                self.textface=self.basicfont.render(self.text,True,self.tcolor)
                self.toleft=max(0,self.textface.get_width()-self.width)
            elif event.key==pygame.K_LEFT:
                self.toleft=max(0,self.toleft-10)
            elif event.key==pygame.K_RIGHT:
                self.toleft=min(max(0,self.textface.get_width()-self.width),self.toleft+10)
            elif event.key==pygame.K_HOME:
                self.toleft=0
            elif event.key==pygame.K_END:
                self.toleft=max(0,self.textface.get_width()-self.width)
        elif event.type==pygame.TEXTINPUT:
            self.text=(self.text+event.text)[:30]
            self.textface=self.basicfont.render(self.text,True,self.tcolor)
            self.toleft=max(0,self.textface.get_width()-self.width)
    def draw(self,root:pygame.Surface)->None:
        if self.focused:pygame.draw.rect(root,self.fcolor,self.pos+self.size,0)
        else:pygame.draw.rect(root,self.bcolor,self.pos+self.size,0)
        root.blit(self.textface,(self.x-self.toleft,self.y+self.height//2-self.textface.get_height()//2))
class button:
    def __init__(self,size:tuple,pos:tuple,color:Union[tuple,str],font:pygame.font.Font,text:str,func,*args)->None:
        self.stat=0 # 0 none, 1 on, 2 down
        self.width,self.height,self.size=size[0],size[1],size
        self.x,self.y,self.pos=pos[0],pos[1],pos
        self.text=text
        self.basicfont=font
        self.func=func
        if len(args)!=0:self.args=list(args)
        else:self.args=None
        self.color=color
    def exec(self)->None:
        self.func(self.args)
    def inside(self,pos:tuple)->bool:
        return self.x<=pos[0]<=self.x+self.width and self.y<=pos[1]<=self.y+self.height
    def DealEvent(self,event:pygame.event.Event)->None:
        if event.type==pygame.MOUSEMOTION:
            if self.stat!=2:self.stat=self.inside(event.pos)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==4 or event.button==5:return
            if self.inside(event.pos):self.stat=2
        elif event.type==pygame.MOUSEBUTTONUP:
            if self.stat!=2:return
            if self.inside(event.pos):
                self.stat=1
                self.exec()
            else:self.stat=0
    def draw(self,root:pygame.Surface)->None:
        if self.stat==2:
            pygame.draw.rect(root,self.color,self.pos+self.size,0)
            _text=self.basicfont.render(self.text,True,(255,255,255))
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
        elif self.stat==1:
            pygame.draw.rect(root,self.color,self.pos+self.size,2)
            _text=self.basicfont.render(self.text,True,self.color)
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
        elif self.stat==0:
            _text=self.basicfont.render(self.text,True,self.color)
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
class checkbutton:
    def __init__(self,size:tuple,pos:tuple,normalcolor:Union[tuple,str],selectcolor:Union[tuple,str],font:pygame.font.Font,text:str,key=None)->None:
        self.key=key
        self.selected=0
        self.stat=0 # 0 none, 1 on, 2 down
        self.width,self.height,self.size=size[0],size[1],size
        self.x,self.y,self.pos=pos[0],pos[1],pos
        self.text=text
        self.basicfont=font
        self.ncolor=normalcolor
        self.scolor=selectcolor
    def inside(self,pos:tuple)->bool:
        return self.x<=pos[0]<=self.x+self.width and self.y<=pos[1]<=self.y+self.height
    def DealEvent(self,event:pygame.event.Event)->None:
        if event.type==pygame.MOUSEMOTION:
            if self.stat!=2:self.stat=self.inside(event.pos)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==4 or event.button==5:return
            if self.inside(event.pos):self.stat=2
        elif event.type==pygame.MOUSEBUTTONUP:
            if self.stat!=2:return
            if self.inside(event.pos):
                self.stat=1
                self.selected^=1
            else:self.stat=0
    def draw(self,root:pygame.Surface)->None:
        color=self.scolor if self.selected else self.ncolor
        if self.stat==2:
            pygame.draw.rect(root,color,self.pos+self.size,0)
            _text=self.basicfont.render(self.text,True,(255,255,255))
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
        elif self.stat==1:
            pygame.draw.rect(root,color,self.pos+self.size,1)
            _text=self.basicfont.render(self.text,True,color)
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
        elif self.stat==0:
            _text=self.basicfont.render(self.text,True,color)
            root.blit(_text,(self.x+self.width//2-_text.get_width()//2,self.y+self.height//2-_text.get_height()//2))
class frontpage:
    def __init__(self)->None:
        def switchpage(args:list)->None:
            self.page=args[0]
            if args[0]==2:
                self.info=self.basicfont.render('',True,'#CCCCFF')
                for button in self.comparebuttons+self.selectbuttons:
                    button.selected=0
                self.comparebuttons[0].selected=1
                self.selectbuttons[0].selected=1
            if args[0]!=3:
                self.show.elements=self.show.indx=[]
                self.show.xsum=self.show.xscroll=0
                self.show.ysum=self.show.yscroll=0
            self.slowdown=1
        def getfont(size:int)->pygame.font.Font:
            return pygame.font.Font('fonts\\simkai.ttf',size)
        def sall(_:None)->None:
            for button in self.checkbuttons:button.selected=1
        def srev(_:None)->None:
            for button in self.checkbuttons:button.selected^=1
        def toff(_:None)->None:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        def cancel(index:list)->None:
            self.restrictions[0].pop(index[0])
            self.restrictions[1].pop(index[0])
            self.cancelbuttons.pop(index[0])
            for i in range(index[0],len(self.cancelbuttons)-1):
                self.cancelbuttons[i].args[0]-=1
        def addres(_=None)->None:
            for sbutton in self.selectbuttons:
                if sbutton.selected:break
            for compare in self.comparebuttons:
                if compare.selected:break
            if 'name' not in sbutton.key:
                if compare.key=='like':
                    self.info=self.basicfont.render('仅字符串型变量可使用\'~~\'(aka \'like\')比较',True,'#CCCCFF')
                    return
                try:float(self.input.text)
                except:
                    self.info=self.basicfont.render('输入有误',True,'#CCCCFF')
                    pygame.display.update()
                    return
            self.restrictions[0].append(self.basicfont.render(sbutton.text+' '+compare.text+' '+self.input.text,True,'#CCCCFF'))
            if compare.key=='like':self.input.text='\'%'+self.input.text+'%\''
            elif 'name' in sbutton.key:self.input.text='\''+self.input.text+'\''
            self.restrictions[1].append(sbutton.key+' '+compare.key+' '+self.input.text)
            self.cancelbuttons.append(button((60,30),(0,0),'#CCFF66',self.basicfont,'删除',cancel,len(self.restrictions[0])-1))
            switchpage((1,))
            self.input.text=''
            self.input.textface=self.input.basicfont.render('',True,self.input.tcolor)
        def lookup(_:None)->None:
            sqltext='select '
            select,restricts,tables,take='',self.restrictions[1].copy(),('','mob','material','dropped','food','','ingredient','','district','locate'),set()
            for button in self.checkbuttons:
                if button.selected:select+=button.key+','
            if select=='':return
            sqltext+=select[:-1]+' from '
            select+=' '.join(restricts)
            temp=('mob.' in select)|(('material.' in select)<<1)|(('food.' in select)<<2)|(('district.' in select)<<3)
            for i in (1,2,3,4,6,8,9):
                if temp&i==i:take.add(tables[i])
            sqltext+=','.join(take)
            if 'dropped' in take:restricts.append('mob.mid=dropped.mid and dropped.tid=material.tid')
            if 'locate' in take:restricts.append('mob.mid=locate.mid and locate.pid=district.pid')
            if 'ingredient' in take:restricts.append('material.tid=ingredient.tid and ingredient.fid=food.fid')
            if len(restricts):sqltext+=' where '+' and '.join(restricts)
            # print(sqltext,'\n');return
            try:self.cur.execute(sqltext)
            except Exception as error:return print(error)
            for line in self.cur.fetchall():
                templine=[]
                for indv in line:
                    try:
                        if indv[8]==0:
                            pic=pygame.image.load(BytesIO(indv)).convert()
                            newface=pygame.transform.scale(pic,(unitwidth*pic.get_width()/pic.get_height(),unitwidth))
                        else:raise Exception()
                    except:newface=self.basicfont.render(str(indv),True,(255,255,255))
                    templine.append(newface)
                self.show.elements.append(templine)
                self.show.ysum+=unitwidth
            try:
                for indv in self.show.elements[0]:
                    self.show.xsum+=150 if indv.get_width()<200 else unitwidth
            except:pass
            print(self.show.xsum)
            self.show.frame=pygame.Surface((self.show.xsum,self.show.ysum))
            self.show.frame.set_alpha(175)
            switchpage((3,))
        pygame.init()
        environ['SDL_IME_SHOW_UI']='1'
        self.page=0
        self.slowdown:bool=0
        self.main=pygame.display.set_mode((1000,765))
        self.background=pygame.transform.scale(pygame.image.load('images/rose.png'),(471,765)).convert()
        self.cursor=pygame.transform.scale(pygame.image.load('images/ifree.png').convert_alpha(),(445*0.07,492*0.07))
        pygame.display.set_caption('心渊梦境图鉴')
        pygame.display.set_icon(pygame.image.load('images/jeanne.png').convert())
        self.background.set_alpha(102)
        self.basicfont=pygame.font.Font('fonts\\simkai.ttf',20)
        self.title=[
            (getfont(30).render('怪物',True,(255,255,255)),(100,100)),
            (getfont(30).render('区域',True,(255,255,255)),(100,540)),
            (getfont(30).render('食材',True,(255,255,255)),(835,100)),
            (getfont(30).render('料理',True,(255,255,255)),(835,360))
        ]
        self.checkbuttons=[
            checkbutton((100,50),(83,140),(137,66,196),'#CC3399',self.basicfont,'怪物编号','mob.mid'),
            checkbutton((100,50),(83,200),(137,66,196),'#CC3399',self.basicfont,'怪物名称','mob.name'),
            checkbutton((100,50),(83,260),(137,66,196),'#CC3399',self.basicfont,'怪物等级','mob.level'),
            checkbutton((100,50),(83,320),(137,66,196),'#CC3399',self.basicfont,'怪物血量','mob.hp'),
            checkbutton((100,50),(83,380),(137,66,196),'#CC3399',self.basicfont,'怪物攻击','mob.atk'),
            checkbutton((100,50),(83,440),(137,66,196),'#CC3399',self.basicfont,'怪物图片','mob.pic'),
            checkbutton((100,50),(83,580),(137,66,196),'#CC3399',self.basicfont,'地区编号','district.pid'),
            checkbutton((100,50),(83,640),(137,66,196),'#CC3399',self.basicfont,'地区名称','district.name'),
            checkbutton((100,50),(818,140),(137,66,196),'#CC3399',self.basicfont,'食材编号','material.tid'),
            checkbutton((100,50),(818,200),(137,66,196),'#CC3399',self.basicfont,'食材名称','material.name'),
            checkbutton((100,50),(818,260),(137,66,196),'#CC3399',self.basicfont,'食材图片','material.pic'),
            checkbutton((100,50),(818,400),(137,66,196),'#CC3399',self.basicfont,'料理编号','food.fid'),
            checkbutton((100,50),(818,460),(137,66,196),'#CC3399',self.basicfont,'料理名称','food.name'),
            checkbutton((100,50),(818,520),(137,66,196),'#CC3399',self.basicfont,'料理图片','food.pic')
        ]
        self.frontbuttons=[
            button((150,50),(795,600),'#CCFF66',getfont(24),'编辑限制条件',switchpage,1),
            button((150,50),(795,670),'#990033',getfont(24),'查询',lookup),
            button((75,50),(57,20),'#0099CC',self.basicfont,'全选',sall),
            button((75,50),(137,20),'#0099CC',self.basicfont,'反选',srev),
            button((150,50),(795,20),'#990033',getfont(24),'退出',toff)
        ]
        self.restbuttons=[
            button((150,50),(60,20),(137,66,196),getfont(24),'返回',switchpage,0),
            button((150,50),(450,680),'#CCFF66',getfont(32),'+',switchpage,2),
            button((150,50),(795,20),'#990033',getfont(24),'退出',toff)
        ]
        self.restrictions:list[list[pygame.Surface],list[str]]=[[],[]]
        self.addbuttons=[
            button((150,50),(60,20),'#CCFF66',getfont(24),'返回',switchpage,1),
            button((150,50),(795,20),'#990033',getfont(24),'退出',toff),
            button((150,50),(425,680),'#CCCCFF',getfont(24),'确认',addres)
        ]
        self.cancelbuttons:list[button]=[]
        self.restposition=[(270,100+i*50) for i in range(10)]
        self.input=entry((200,30),(750,350),'#FFFFFF','#CCCCFF','#000000',self.basicfont)
        self.selectbuttons=[
            checkbutton((100,50),(83,100),'#CCCCFF','#CC3399',self.basicfont,'怪物编号','mob.mid'),
            checkbutton((100,50),(83,160),'#CCCCFF','#CC3399',self.basicfont,'怪物名称','mob.name'),
            checkbutton((100,50),(83,220),'#CCCCFF','#CC3399',self.basicfont,'怪物等级','mob.level'),
            checkbutton((100,50),(83,280),'#CCCCFF','#CC3399',self.basicfont,'怪物血量','mob.hp'),
            checkbutton((100,50),(83,340),'#CCCCFF','#CC3399',self.basicfont,'怪物攻击','mob.atk'),
            checkbutton((100,50),(83,400),'#CCCCFF','#CC3399',self.basicfont,'地区编号','district.pid'),
            checkbutton((100,50),(83,460),'#CCCCFF','#CC3399',self.basicfont,'地区名称','district.name'),
            checkbutton((100,50),(83,520),'#CCCCFF','#CC3399',self.basicfont,'食材编号','material.tid'),
            checkbutton((100,50),(83,580),'#CCCCFF','#CC3399',self.basicfont,'食材名称','material.name'),
            checkbutton((100,50),(83,640),'#CCCCFF','#CC3399',self.basicfont,'料理编号','food.fid'),
            checkbutton((100,50),(83,700),'#CCCCFF','#CC3399',self.basicfont,'料理名称','food.name')
        ]
        self.comparebuttons=[
            checkbutton((100,50),(450,200),'#CCCCFF','#CC3399',self.basicfont,'>','>'),
            checkbutton((100,50),(450,260),'#CCCCFF','#CC3399',self.basicfont,'<','<'),
            checkbutton((100,50),(450,320),'#CCCCFF','#CC3399',self.basicfont,'=','='),
            checkbutton((100,50),(450,380),'#CCCCFF','#CC3399',self.basicfont,'>=','>='),
            checkbutton((100,50),(450,440),'#CCCCFF','#CC3399',self.basicfont,'<=','<='),
            checkbutton((100,50),(450,500),'#CCCCFF','#CC3399',self.basicfont,'~~','like')
        ]
        self.info=self.basicfont.render('',True,'#CCCCFF')
        self.fetchedbuttons=[
            button((150,50),(60,20),(137,66,196),getfont(24),'返回',switchpage,0),
            button((150,50),(795,20),'#990033',getfont(24),'退出',toff)
        ]
        self.conn=sql.connect('data/Atlas.atl')
        self.cur=self.conn.cursor()
        self.show=frame((100,100))
        pygame.key.set_repeat(500,50)
    def mainloop(self)->None:
        while True:
            if self.slowdown==2:
                for i in range(100):
                    pygame.event.clear()
                    self.main.fill((0,0,0))
                    self.background.set_alpha(102-i)
                    self.main.blit(self.background,(264.5,0))
                    self.main.blit(self.cursor,pygame.mouse.get_pos())
                    pygame.display.update()
                    pygame.time.wait(5)
                for i in reversed(range(100)):
                    pygame.event.clear()
                    self.main.fill((0,0,0))
                    self.background.set_alpha(102-i)
                    self.main.blit(self.background,(264.5,0))
                    self.main.blit(self.cursor,pygame.mouse.get_pos())
                    pygame.display.update()
                    pygame.time.wait(5)
                self.slowdown=0
            else:
                self.main.fill((0,0,0))
                self.main.blit(self.background,(264.5,0))
            event=pygame.event.wait()
            if event.type==pygame.QUIT:break
            if self.page==0:
                for t in self.title:self.main.blit(t[0],t[1])
                for button in self.checkbuttons+self.frontbuttons:
                    button.DealEvent(event)
                    button.draw(self.main)
            elif self.page==1:
                for button in self.restbuttons+self.cancelbuttons:button.DealEvent(event)
                for cstr,button,pos in zip(self.restrictions[0],self.cancelbuttons,self.restposition):
                    self.main.blit(cstr,pos)
                    button.x,button.y,button.pos=700,pos[1]-5,(700,pos[1]-5)
                for button in self.restbuttons+self.cancelbuttons:button.draw(self.main)
            elif self.page==2:
                if event.type==pygame.MOUSEBUTTONUP:
                    for button in self.selectbuttons:
                        if button.stat!=2 or not button.inside(event.pos):continue
                        for item in self.selectbuttons:item.selected=0
                        break
                    for button in self.comparebuttons:
                        if button.stat!=2 or not button.inside(event.pos):continue
                        for item in self.comparebuttons:item.selected=0
                        break
                for button in self.selectbuttons+self.comparebuttons+self.addbuttons:
                    button.DealEvent(event)
                    button.draw(self.main)
                self.input.DealEvent(event)
                self.input.draw(self.main)
                self.main.blit(self.info,(950-self.info.get_width(),600))
            elif self.page==3:
                self.show.DealEvent(event)
                self.show.draw(self.main)
                for button in self.fetchedbuttons:
                    button.DealEvent(event)
                    button.draw(self.main)
            self.main.blit(self.cursor,pygame.mouse.get_pos())
            pygame.display.update()
        pygame.quit()
        self.cur.close()
        self.conn.close()
if __name__=='__main__':
    frontpage().mainloop()
{'''tables'''
}
{# mob
# cur.execute(
#     '''
#     create table mob(
#         mid tinyint,
#         name char(10),
#         level tinyint,
#         hp decimal(6,1),
#         atk decimal(4,1),
#         pic blob,
#         primary key(mid)
#     )
#     '''
# )
}
{# district
# cur.execute(
#     '''
#     create table district(
#         pid tinyint,
#         name char(5),
#         primary key(pid)
#     )
#     '''
# )
}
{# material
# cur.execute(
#     '''
#     create table material(
#         tid tinyint,
#         name char(5),
#         pic blob,
#         primary key(tid)
#     )
#     '''
# )
}
{# food
# cur.execute(
#     '''
#     create table food(
#         fid tinyint,
#         name char(7),
#         pic blob,
#         primary key(fid)
#     )
#     '''
# )
}
{# locate
# cur.execute(
#     '''
#     create table locate(
#         mid tinyint,
#         pid tinyint,
#         primary key(mid,pid),
#         foreign key(mid) references mob(mid),
#         foreign key(pid) references district(pid)
#     )
#     '''
# )
}
{# dropped
# cur.execute(
#     '''
#     create table dropped(
#         mid tinyint,
#         tid tinyint,
#         primary key(mid,tid),
#         foreign key(mid) references mob(mid),
#         foreign key(tid) references material(tid)
#     )
#     '''
# )
}
{# ingredient
# cur.execute(
#     '''
#     create table ingredient(
#         tid tinyint,
#         fid tinyint,
#         primary key(tid,fid),
#         foreign key(tid) references material(tid),
#         foreign key(fid) references food(fid)
#     )
#     '''
# )
}