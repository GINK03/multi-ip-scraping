import os
import json


data = os.popen('aws ec2 describe-instances').read()


f = open('aws_ip.txt', 'w')
obj = json.loads(data)

for iobj in obj['Reservations']:
  for insta in iobj['Instances']:
    insta = insta
    lifetime = insta.get('InstanceLifecycle')
    public = insta.get('PublicIpAddress')
    #publicIpAddress = insta['PublicIpAddress']
    #print( insta )
    line = '{} {}'.format(lifetime, public)
    print( line )
    
    if lifetime == 'spot' and public is not None:
      f.write( line + '\n')

