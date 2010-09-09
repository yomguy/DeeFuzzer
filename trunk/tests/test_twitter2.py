#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import twitter

# DeeFuzzer consumer keys

consumer_key    = 'ozs9cPS2ci6eYQzzMSTb4g'
consumer_secret = '1kNEffHgGSXO2gMNTr8HRum5s2ofx3VQnJyfd0es'

# Token keys

# YomGuy
#access_token_key = '18295650-30TgtgZTrWuoS0lkYx4W2W3mDKbc1wkl85Q70fRUo'
#access_token_secret = 'lNArajV6ENBHIsDod9EPxupkRnlxBCPJxrPOpFPR8'

# DeeFuzz Radio
access_token_key = '76728330-6g3ISHcbGiXDICRdYCOmQtfZioZ2M8gsHH9HqALXd'
access_token_secret = 'YHx0Dc7gpCgkVUouURdByZ43ZNStCBA1ZUhKJUklo'


api = twitter.Api(username=consumer_key,
                  password=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret)

#print 'Friends :'
#friends = api.GetFriends()
#print [u.name for u in friends]

#followers = []
#for page in range(0,2):
    #try:
        #f = api.GetFollowers(page=page)
        #for follower in f:
            #followers.append(follower)
    #except:
        #raise 'No page :', page

#print 'Followers :'
#print [u.name for u in followers]
#print 'Length : ', len(followers)

#print 'Mentions :'
#mentions = api.GetMentions()
#print [(m.user.name, m.text) for m in mentions]

print 'Statuses :'
statuses = api.GetUserTimeline('deefuzz_radio')
print [(s.user.id, s.user.name, s.text, s.created_at) for s in statuses]
