#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sys,time
from collections import Counter
from glob import glob

font = {'size'   : 20}
matplotlib.rc('font',**font)

DCOLORS=['b','g','r','c','m','y','0.5','#1B7677','w','#8B0000']

def do_histplot(DATA,USERS,TITLE,FNAME,FSIZE=(14,10),YLABEL="Häufigkeit",KEYGEN=lambda x:x,
        LOFFSET=0.,GROUPING=None):
    assert len(DATA[0])-1==len(USERS)
    # group data if possible and neccessary
    if GROUPING!=None:
        if len(USERS)>GROUPING[0]:
            crit=sorted([(u,GROUPING[2][u]) for u in range(len(users))],key=lambda x:x[1],reverse=True)
            sel=([i[0]+1 for i in crit[:GROUPING[1]]],[i[0]+1 for i in crit[GROUPING[1]:]])
            USERS=[USERS[j[0]] for j in crit[:GROUPING[1]]] \
                    +['Rest']
            DATA=[[i[0]] \
                    +[i[j] for j in sel[0]] \
                    +[sum([i[j] for j in sel[1]])] for i in DATA]
    fig=plt.figure(figsize=FSIZE)
    off=np.zeros(len(DATA))
    for i in range(len(DATA[0])-1):
        tmp=np.array([j[1+i] for j in DATA])
        plt.barh(range(len(DATA)),tmp,left=off,height=1.0,color=DCOLORS[i%len(DCOLORS)],
                label=USERS[i],edgecolor='k',zorder=10)
        off+=tmp
    plt.legend(loc=0)
    plt.yticks([i+LOFFSET for i in range(len(DATA))],[KEYGEN(i[0]) for i in DATA])
    plt.ylim(-0.5,len(DATA)-0.5)
    plt.xlabel(YLABEL)
    plt.title(TITLE)
    plt.grid(zorder=-10)
    fig.tight_layout()
    plt.savefig(FNAME)
    plt.close(fig)
    return None

# reorder data for better readability in pie chart
# DATA    - Data
# LABELS  - corresponding labels
# returns - (DATA,LABELS)
def pie_reorder(DATA,LABELS):
    tmp=sorted([[DATA[i],LABELS[i]] for i in range(len(DATA))],key=lambda x: x[0])
    NDATA=[]
    NLABELS=[]
    sw=False
    while len(tmp)>0:
        idx=0 if sw else -1
        NDATA.append(tmp[idx][0])
        NLABELS.append(tmp[idx][1])
        del tmp[idx]
        sw=not sw
    return NDATA,NLABELS

# generate a pie plot
# DATA     - data to be displayed
# LABELS   - Labels
# TITLE    - title
# FNAME    - target file name
# FSIZE    - (Optional) change figure size
# grouping - (Optional) criteria for grouping: (min#, #ungrouped)
def do_pieplot(DATA,LABELS,TITLE,FNAME,FSIZE=(10,10),grouping=(15,13)):
    assert len(DATA)==len(LABELS)
    if len(DATA)>grouping[0]:
        top=sorted([(DATA[i],LABELS[i]) for i in range(len(DATA))],key=lambda x:x[0],reverse=True)
        DATA=[i[0] for i in top[:grouping[1]]]+[sum([i[0] for i in top[grouping[1]:]])]
        LABELS=[i[1] for i in top[:grouping[1]]]+['Rest']
    # rearrange data
    if len(DATA)>4:
        DATA,LABELS=pie_reorder(DATA,LABELS)
    # do plotting
    fig=plt.figure(figsize=FSIZE)
    l=plt.pie(  DATA,labels=LABELS,labeldistance=0.5,radius=1.1,colors=DCOLORS,
                pctdistance=0.2,shadow=True,explode=[0.05 for i in DATA],startangle=45)
    c=0
    for i in l[1]:
        i.set_bbox(dict(facecolor=DCOLORS[c%len(DCOLORS)],alpha=0.7))
        i.set_fontsize(16)
        i.set_fontweight(1000)
        p=i.get_position()
        i.set_position((p[0]*0.9,p[1]*1.6))
        c+=1
    plt.title(TITLE)
    plt.savefig(FNAME)
    plt.close(fig)
    return None

def parse_line(l):
    ret=[]
    l=l.split('-')
    if len(l)<2:
        return ['app',list(filter(lambda x: len(x)>0, ' '.join(l).split(' ')))]
    try:
        tmp=(time.strptime(l[0],'%d/%m/%Y, %H:%M '))
    except:
        try:
            tmp=(time.strptime(l[0],'%d.%m.%y, %H:%M '))
        except:
            return ['app',list(filter(lambda x: len(x)>0, ' '.join(l).split(' ')))]
    ret.append(tmp)
    orig=l # TODO remove
    l=('-'.join(l[1:])).split(':')
    if len(l)<2:
        return None
    if l[1]==' <Media omitted>' or l[1]==' <Medien weggelassen>':
        return None
    name=l[0].split(' ')[1]
    if name[-3:]=='+49':
        name=l[0]
    ret.append(name)#(l[0].replace(' ',''))
    ret.append(list(filter(lambda x: len(x)>0, (':'.join(l[1:])).split(' '))))
    return ret

def concat(lines):
    tmp=[]
    cchain=[]
    for i in lines:
        if i[0]=='app':
            cchain+=i[1]
        else:
            tmp.append([i[0],i[1],i[2]+cchain])
            cchain=[]
    return tmp

def rmdot(s):
    if len(s)<2:
        return s
    if s[-1]=='.' and s[-2]!='.':
        return s[:-1]
    return s

def gen_wordhist(fid,data,users):
    hists=[Counter([rmdot(i.lower()) for sub in filter(lambda x: x[1]==u,data) for i in sub[2] if (len(i)>0 and i!='.')]) for u in users]
    group_crit=[sum([h[1] for i in h]) for h in hists]
    gen_wordhist_sub(fid+'_wh',hists,users)
    for ud in hists:
        for word in WORD_BLACKLIST:
            ud[word]=0
    gen_wordhist_sub(fid+'_wh_filtered',hists,users)

def gen_wordhist_sub(fid,data,users,nword=25):
    fhist=sum(data,Counter()).most_common(nword)
    group_crit=[sum([h[i] for i in h]) for h in data]
    histdat=[[word]+[data[u][word] for u in range(len(users))] for word in map(lambda x:x[0], fhist)]
    do_histplot(histdat,users,fid,fid+'.png',GROUPING=(10,8,group_crit))

def gen_anteile(fid,data,users):
    umsg={u:list(filter(lambda x:x[1]==u,data)) for u in users}
    msgcount=[len(list(umsg[u])) for u in users]
    wrdcount=[sum([len(w[2]) for w in umsg[u]]) for u in users]
    chrcount=[sum([len(''.join(w[2])) for w in umsg[u]]) for u in users]
    do_pieplot(msgcount,[users[u]+'\n%u msgs'%(msgcount[u]) for u in range(len(users))],
            fid+'\nmessages per user',fid+'_msg.png')
    do_pieplot(wrdcount,[users[u]+'\n%u wrds'%(wrdcount[u]) for u in range(len(users))],
                fid+'\nwords per user',fid+'_wrd.png')
    do_pieplot(chrcount,[users[u]+'\n%u chrs'%(chrcount[u]) for u in range(len(users))],
                fid+'\ncharacters per user',fid+'_chr.png')

# check sysargs
if len(sys.argv)<2:
    print('usage:\n whatstat file.txt [file2.txt ..]')

with open('words_blacklist.txt') as f:
    WORD_BLACKLIST=[l.replace('\n','') for l in f]
print('%i filtered words loaded'%(len(WORD_BLACKLIST)))

# main loop
for fstring in sys.argv[1:]:
    for fname in glob(fstring):
        fid=fname.split('.')
        fid=fid[0] if len(fid)==1 else ''.join(fid[:-1])
        print(fid)
        # read data and do preprocessing
        f=open(fname)
        lines=[parse_line(i[:-1]) for i in f if len(i)>1]
        lines=reversed(list(filter(lambda x: x!=None, lines)))
        lines=concat(lines)
        users=list(sorted(set(map(lambda x: x[1],lines))))
        # plot results
        print(users)
        gen_wordhist(fid,lines,users)
        gen_anteile(fid,lines,users)
