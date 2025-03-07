#!/usr/bin/python3
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdgetnoportpy import etcdget as getnoport
from etcdput import etcdput as put
from etcddel import etcddel as dels 
from ast import literal_eval as mtuple
from socket import gethostname as hostname

allusers= []
leader, leaderip, myhost, myhostip = '','','',''


def grpfninit(ldr,ldrip,hst,hstip,pprt='-1'):
 global allusers, leader ,leaderip, myhost, myhostip,pport
 leader, leaderip, myhost, myhostip, pport = ldr, ldrip, hst, hstip, pprt
 return
#def thread_add(*user):

def thread_add(user,syncip,pullsync='pullavail'):
 global allusers, leader ,leaderip, myhost, myhostip
 username=user[0].replace('usersigroup/','')
 if 'Everyone' == username:
  return
 groupusers=user[1].split('/')[2]
 if groupusers=='no':
  groupusers='users'
 else:
  groupusers='users'+groupusers
 try:
  userigroup=user[1].split(':')
  userid=userigroup[0]
  usergd=userigroup[1]
 except:
    return
 cmdline=['/TopStor/UnixAddGroup',leaderip, username, groupusers, pullsync, userid,usergd, 'system']
 put(syncip, user[0],user[1])
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)

#def thread_del(*user):
def thread_del(username,pullsync='pullavail'):
 global allusers, leader ,leaderip, myhost, myhostip
 if 'Everyone' == username:
  return
 print(username)
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelGroup',leaderip, username,'system',pullsync]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def groupsyncall(tosync=''):
 global allusers, leader ,leaderip, myhost, myhostip, pport
 global myusers
 if 'pullsync' in tosync:
    allusers=getnoport(leaderip,pport,'usersigroup','--prefix')
 else:
    allusers=get(leaderip,'usersigroup','--prefix')
 if myhost in leader:
    syncip = leaderip
 else:
    syncip = myhostip
 myusers=get(syncip,'usersigroup','--prefix')
 print(';;;;;',myusers,allusers)
 threads=[]
 if '_1' in allusers:
  allusers=[]
 if '_1' in myusers:
  myusers=[]
 for user in myusers:
  if user not in allusers:
   user = user[0].split('/')[1] 
   thread_del(user)
   dels(syncip, user[0])

 for user in allusers:
  print(user)
  thread_add(user,syncip)
  put(syncip, user[0],user[1])
   
def onegroupsync(oper,usertosync,tosync='pullavail'):
 global allusers, leader ,leaderip, myhost, myhostip, pport
 if myhost in leader:
    syncip = leaderip
 else:
    syncip = myhostip
 if oper == 'Add':
    if 'pullsync' in tosync:
        user=getnoport(leaderip, pport, 'usersigroup', usertosync)[0]
    else:
        user=get(leaderip,'usersigroup', usertosync)[0]
    thread_add(user,syncip)
 else:
    user = usertosync
    thread_del(user,tosync)
    
 
  
if __name__=='__main__':
 with open('/root/sync2','w') as f:
  f.write('Starting\n')

 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
 leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
 leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
 myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
 myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 if len(sys.argv[1:]) < 2:
    print(' syncing all groups')
    groupsyncall(*sys.argv[1:])
 else:
    onegroupsync(*sys.argv[1:])
