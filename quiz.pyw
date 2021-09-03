#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  quiz.py
#  
#  Copyright 2021  <pi@NYNY>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import json
import random
import logging
from textwrap import wrap,fill
import argparse as ap
import tkinter as  tk
from tkinter import ttk
import tkinter.filedialog as filedialog

log = logging.getLogger(__name__)
logging.basicConfig()

class Quiz:
    def __init__(self, quizfile='IP Office ACSS.json',*kwargs):
        self.load_quiz(quizfile)
        log.info('Initialised Sub-Classs Quiz')
    
    def load_quiz(self, quizfile):
        with open(quizfile, 'r') as datafile:
            data  =datafile.readlines()
            q, a, c = data
            self.questions = json.loads(q)
            log.info(f'{len(self.questions)} Questions Imported')
            self.answers = json.loads(a)
            self.correct = json.loads(c)

    def run(self):
        while True:
            count=int(input(
                f'How many test questions (max:{len(self.questions)}) :'))
            score = 0
            qlist = [_ for _ in self.questions]
            random.shuffle(qlist)
            for q in qlist[:count]:
                print(f'\nQuestion #{q}\n')
                print(self.question(q))
                print()
                for answer in self.answers[q]:
                    print(answer)
                print()
                answers=input('Please select your answer(s) separated by "," if necessary: ').upper()
                if answers.upper().startswith('Q'):
                    count=qlist.index(q)
                    log.debug(f'count={count}')
                    break
                ans=answers.split(',')
                if self.check(q,ans):
                    score += 1
                    print('Your Answers Agreed with Avaya')
                else:
                    print('your Answers did not agree with Avaya')
                log.debug(f'Running total: {score}')
            try:
                print(f'\nFinal Score:{score}/{count} - {score/count*100}%')
                if score/count >+.75:
                    print('PASS!')
            except ZeroDivisionError:
                print('You did not answer any questions!')
                
            retry=input('Test Again? ')
            if retry.upper()[0] != 'Y':
                break
            
    def question(self,q):
        questions=self.questions[q].splitlines()
        question='\n'.join([fill(_) for _ in questions])
#        print(question)
        return question
        
    def check(self, q,ans):
        correct=self.correct[q].split(',')
        log.debug(f'ans:{ans}, Correct={correct}')
        if len(ans) == len(correct):
            for answer in correct:
                log.debug(f'answer {answer}, {answer in ans}')
                if answer not in ans:
                    log.debug(f'Correct answer missing')
                    break
            else:
                log.debug(f'Else condition of for loop so answers all present')
                return True
#        print(f'Incorrect number of answers')
        log.debug('correct answer missing or incorrect number of answers')
        return False
    
class Gui(tk.Tk):
    
    def __init__(self,quizfile='IP Office ACSS.json',title='ACSS Quiz'):
        super().__init__()
        self.quiz = quiz = Quiz()
        log.debug(f'{id(self.quiz)},{id(quiz)}')
        self.title(title)
        self.geometry('640x400')
        self.resizable(False,True)
        self.centre(self)
        frame1 = ttk.Frame(self, width=80)
        self.frame2 = ttk.Frame()
        self.frame3 = ttk.Frame(self, width=80)
        frame1.pack()
        self.frame2.pack()
        self.frame3.pack()
        self.prog=ttk.Frame(self.frame2)
        self.frame3.pack()
        row =column = 0
        self.quizname=ttk.Entry(frame1)
        self.quizname.insert(0,quizfile)
        self.quizname.grid(row=row,column=column)
        column += 1
        self.load_new=ttk.Button(frame1, command=self.load, text='New Quiz')
        self.load_new.grid(row=row,column=column)
        row,column = row+1, 0
        self.count=ttk.Spinbox(
            frame1, width=4, from_=1, to=len(quiz.questions))
        self.count.set(60)
        self.count.grid(row=row, column=column)
        column += 1
        self.start = ttk.Button(frame1, command=self.start, text='start')
        self.start.grid(row=row,column=column)
        self.qbox = tk.Text(self, height=6, width=80)
        self.qbox.pack()
 
    def load(self):
        log.debug('File requester goes here')
        filename = filedialog.askopenfilename()
        self.quizname.delete(0, 'end')
        self.quizname.insert(0, filename)
        self.quiz.load_quiz(filename)
        
        
    def load_quiz(self):
        self.quiz.load_quiz(self.quizname.get())
    
    def get_question(self,qlist):
        for q in qlist:
            yield q
            
    def start(self):
        log.debug('start quiz')
        self.current = 0
        self.correct = 0
        self.load_quiz()
        self.max=count = int(self.count.get())
        qlist=[_ for _ in self.quiz.questions]
        random.shuffle(qlist)
        log.debug(qlist)
        self.qlist = self.get_question(qlist[:count])
        self.prog.destroy()
        self.prog = ttk.Frame(self.frame2)
        self.prog.pack()
        label=ttk.Label(self.prog,text='Progress')
        label.grid(row=0, column=0)
        self.progress=ttk.Progressbar(self.prog,orient='horizontal', length=300)
        self.progress.grid(row=0, column=1)
        self.qcount=ttk.Label(self.prog, text=f"0/{self.max}")
        self.qcount.grid(column=2, row=0)
        label=ttk.Label(self.prog,text='Score')
        label.grid(row=1, column=0)
        self.score=ttk.Progressbar(self.prog,orient='horizontal', length=300)
        self.score.grid(row=1, column=1)
        self.score_text=tk.Label(self.prog, text=f'0/{self.max}')
        self.score_text.grid(row=1, column=2)
        self.next_question()
    
    def next_question(self):
        self.current += 1
        log.debug('next question')
        try:
            self.q = next(self.qlist)
            log.debug(f'Question id {self.q}')
            self.qbox.delete('1.0','end')
            self.frame3.destroy()
            self.frame3 = ttk.Frame(self, width=80)
            self.frame3.pack(side='left')
            question="\n".join([f'Qusetion {self.q}', self.quiz.question(self.q)])
            self.qbox.insert('1.0', question)
            self.answers = {}
            self.state = {}
            self.qcount['text']=f'{self.current-1}/{self.max}'
            for i,answer in enumerate(self.quiz.answers[self.q]):
                self.state[i]=tk.IntVar()
                self.answers[i]=tk.Checkbutton(self.frame3, text=fill(answer), 
                                                variable=self.state[i],
                                                anchor='w',
                                                )
                self.answers[i].pack( anchor='w')
                self.answers[i].deselect()
            enter=ttk.Button(self.frame3,command=self.enter, text='Enter')
            enter.pack(anchor='w')  
        except StopIteration:
            self.frame3.destroy()
            self.qbox.delete('1.0', 'end')
            log.debug(f'Display Scores {self.correct}, {self.max}')
            percent=self.correct/self.max*100
            result = f'You have scored {self.correct} out of {self.max} {percent}%'
            if percent >= 75:
                result += "\n Congratulations that would be a PASS"
            self.alert("Results", result)
            
    def enter(self,*args):
        log.debug(f'Count={self.current}')
        log.info('Enter!')
        self.progress['value'] = self.current/self.max*100
        ans=[]
        opt=('A', 'B', 'C', 'D', 'E', 'F', 'G')
        for i in self.state:
            if self.state[i].get():
                ans.append(opt[i])
        log.debug(f"answers={ans}")
        if self.quiz.check(self.q,ans):
            log.debug('correct Answer')
            self.correct += 1
        else:
            message = f'''Avaya do not agree with your answer
            Avaya's answer(s) are {" ".join(self.quiz.correct[self.q])}'''
            self.alert('Incorrect',message)
            log.debug('continue as normal')
        percent = self.correct/self.max*100
        self.score['value'] = percent
        self.score_text['text'] = f'{self.correct}/{self.max} ({int(percent)}%)'
        log.debug('goto next question')
        self.next_question()

    def run(self):
        self.mainloop()

    def alert (self, title=None, message=None):
        win=tk.Toplevel()
        win.wm_title(title)
        label = ttk.Label(win,text=message)
        label.pack()
        button=ttk.Button(win, text='OK', command=win.destroy)
        button.pack()
    
        self.centre(win, 200, 100)
        self.wait_window(win)

    def centre(self, win, width=640, height=400):
        screen_width = win.winfo_screenwidth()
        screen_height=win.winfo_screenheight()
        log.debug(f'Screen {screen_width},{screen_height}')
        log.debug(f'window {width},{height}')

        x=int(screen_width/2 - width/2)
        y=int(screen_height/2 - height/2)
        win.geometry(f'+{x}+{y}')


def main(args):
    if args.cli:
        quiz = Quiz()
    else:
        log.debug('Gui mode selected')
        quiz = Gui()
    quiz.run()
    return 0

if __name__ == '__main__':
    import sys
    parser=ap.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-c','--cli', default = False,
                        action='store_const',
                        const=True,
                        )
    parser.add_argument('-d','--debug', default= False,
                        action='store_const',
                        const=True,
                        )
    args=parser.parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)
    log.info('Debug log enabled')
    sys.exit(main(args))
