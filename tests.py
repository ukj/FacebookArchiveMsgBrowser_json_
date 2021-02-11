# https://www.python-course.eu/tkinter_layout_management.php
# https://stackoverflow.com/questions/48731746/how-to-set-a-tkinter-widget-to-a-monospaced-platform-independent-font
#https://www.delftstack.com/howto/python-tkinter/how-to-set-font-of-tkinter-text-widget/

import tkinter as tk
from tkinter import font


quote_insert = f'''
HAMLET:
    https://et.m.wikipedia.org/wiki/Olla_v%C3%B5i_mitte_olla
-------------------------------------
Olla või mitte olla?- See on küsimus!
Mis oleks üllam: Vaimus taluda
kõik nooled, mida vali saatus paiskab...
või tõstes relvad hädamere vastu
vaev lõpetada? Surra, magada.
Muud midagi! Sest nõnda uinude
kaoks hingepiin ja kõik need tuhat häiret,
mis meie liha pärib looduselt.
See oleks lõpetus, mis hardasti
on ihaldatav. Surra, magada?
-Jah magada! Võib olla undki näha.
Siin ongi konks! Sest see, mis unenäod
meil võivad tulla selles surmaunes
kui maise möllu puntrast pääseme,
see paneb kõhklema. Siin peitub põhjus,
miks viletsusel iga on nii pikk.
Kes taluks aja piitsutust ja torkeid,
rõhuja kalkust, kõrgi solvamisi,
põlatud armu piinu, kohtu aeglust
ja võimu jultumust ning jalahoope,
mis malbe teenekus saab väärituilt
kui ennast igaveseks vabastada
võiks palja pussiga?!
Kes koormat kannaks ja higistaks
ning oigaks elu vaevus,
kui kartus millegi ees pärast surma
sel uurimata maal, kust ükski rändur ei tule tagasi;
ei rabaks tahet, mis pigem talub tuntud halbusi,
kui pageb teiste, tundmatute juurde?
Nii kaalutlus teeb pelgureiks meid kõiki ja
südiduse loomulikust jumest saab nukra mõtte põdur kahvatus
ning lennukad ja tähtsad ettevõtted
teelt targutuste tõttu kalduvad ja kaotavad teo nime...
'''.split("\n")

counter = 0 
def counter_label(label):
    counter = 0
    def count():
        global counter
        counter += 1
        label.config(text=str(counter))
        label.after(1000, count)
    count()

t_counter=0
def textbox_update():
    global quote_insert, T, t_counter
    T.insert(tk.END, quote_insert[t_counter])
    T.insert(tk.END, "\n\n")
    if t_counter == len(quote_insert)-1:
        t_counter = 0
    else:
        t_counter +=1
        
        
        

    
    


#root = tk.Tk()
root.title("Counting Seconds")
label = tk.Label(group_1, fg="dark green")
counter_label(label)
