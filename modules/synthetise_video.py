import sys
from aip import AipSpeech

APP_ID='31180875'
API_KEY='2nnktWvBHaBa3drUiLqrELLB'
SECRET_KEY='sGSTdQj8KVr17uGZG2TVcCGMVe31Eejd'

if __name__=="__main__":
    client=AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    text_input=sys.argv[1]

    result=client.synthesis(text_input, 'en',1,{
        'vol':5,
        'spd':5,
        'pit':9,
        'per':4,#女0 男1 萝莉4 逍遥3
        })

    if not isinstance(result, dict):
            with open('/Users/yixinzhang/visual_sys/syn_audio/syn_audio.mp3','wb') as fle:
                fle.write(result)
    
