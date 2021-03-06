#capstone/src
import json
import sys
import tweepy
from kafka import KafkaProducer, KafkaClient
from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener
from configparser import ConfigParser
from utils import team_dict

class TstreamListener(StreamListener):
    def __init__(self, api):
        self.api = api
        super(StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    def on_data(self, data):
        """
        Called whenever new data arrives as live stream
        """
        text = json.loads(data)['text'].encode('utf-8')
        print (text)
        try:
            self.producer.send('twitterstream', data)
        except Exception as e:
            print (e)
            return False
        return True

    def on_error(self, status_code):
        print ("Error received in kafka producer")
        return True #don't kill the stream

    def on_timeout(self):
        return True

if __name__ == '__main__':
    PROJECT_HOME = '/home/ubuntu/capstone/'
    #authenticate
    config = ConfigParser()
    config.read(PROJECT_HOME + '.config/.credentials')
    consumer_key = config.get('auth', 'consumer_key')
    consumer_secret = config.get('auth', 'consumer_secret')
    access_token = config.get('auth', 'access_token')
    access_token_secret = config.get('auth', 'access_token_secret')

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    
    stream = Stream(auth, listener=TstreamListener(api))
 
    tracked = []
    for team in team_dict.keys():
        tracked.extend(team_dict[team]) 
    stream.filter(track=tracked, languages=['en'])
