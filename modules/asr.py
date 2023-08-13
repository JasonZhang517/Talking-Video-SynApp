import os
import datetime
import json
import math
import requests
import pprint
import fire
import json
import utils
from aip import AipSpeech
from pathlib import Path

productId = "278589295"
apiKey = "cc7d7c3a35654ed6bc7df213c78f9522"
baseUrl = "https://lasr.duiopen.com/lasr-file-api/v2/"

APP_ID='31180875'
API_KEY='2nnktWvBHaBa3drUiLqrELLB'
SECRET_KEY='sGSTdQj8KVr17uGZG2TVcCGMVe31Eejd'

client=AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def main(filename, task=0):
    """
    task: 0 - ASR submission, 1 - retrieve ASR results
    """
    
    if task:
        # with open(Path(Path(filename).stem + "_slices") / "taskId.txt", "r") as f:
            # taskId = f.readline().split(":")[1].strip()
        with open("taskIds.txt", "r") as f:
            for line in f.readlines():
                key, taskId = line.strip().split()
                if key == Path(filename).name:
                    break

        url = baseUrl + f"task/{taskId}/progress?productId={productId}&apiKey={apiKey}"
        response = json.loads(requests.get(url).text)
        if response["data"]["progress"] != 100:
            print(f"The task {taskId} has not finished!")
            exit(1)
        url = baseUrl + f"task/{taskId}/result?productId={productId}&apiKey={apiKey}"
        result = json.loads(requests.get(url).text)
        # outfile = open("./result.txt", 'a', encoding='UTF-8')
        print("Merged recognition results: ")
        res=utils.merge_asr_segments(result["data"]["result"])[0]["onebest"]
        print(res)
        data_to_be_translated={'doctype': 'json', 'type': 'ZH_CN2EN','i': res}
        r=requests.get("http://fanyi.youdao.com/translate",params=data_to_be_translated)
        youdao_result=r.json()
        translate_result=youdao_result['translateResult'][0][0]['tgt']
        print(translate_result)
        result=client.synthesis(translate_result, 'en',1,{
            'vol':5,
            'spd':5,
            'pit':9,
            'per':0,#女0 男1 萝莉4 逍遥3
        })
        if not isinstance(result, dict):
            with open('/mnt/xlancefs/home/gyh17/3D_face/ASR/syn_audio.mp3','wb') as fle:
                fle.write(result)
        #pprint.pprint(utils.merge_asr_segments(result["data"]["result"]))
        # outfile.write(pprint.pformat(utils.merge_asr_segments(result["data"]["result"])))
        # outfile.close()
        exit(0)

    url = baseUrl + f"audio?productId={productId}&apiKey={apiKey}"

    response = json.loads(requests.post(url,
                                        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                                        data={"audio_type": "wav", "slice_num": "1"}).text)
    if response["errno"] != 0:
        print(response)
        print("Creating audio failed!")
        return 1

    audioId = response["data"]["audio_id"]
    url = baseUrl + f"audio/{audioId}/slice/0?productId={productId}&apiKey={apiKey}"
    response = json.loads(requests.post(url, files={"file": open(filename, "rb")}).text)
    if response["errno"] != 0:
        print("Uploading audio failed!")
        return 1
        print("Finishing uploading slice {}".format(response["data"]["slices"]))

    url = baseUrl + f"task?productId={productId}&apiKey={apiKey}"
    response = json.loads(requests.post(url,
                                        data={"audio_id": audioId},
                                        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF8"}).text)

    if response["errno"] != 0:
        print("Creating task failed!")
        return 1
    
    key2taskId = {}
    if Path("taskIds.txt").exists():
        with open("taskIds.txt", "r") as f:
            for line in f.readlines():
                key, taskId = line.strip().split()
                key2taskId[key] = taskId
    
    if Path(filename).name in key2taskId:
        with open("taskIds.txt", "a") as f:
            f.write("{} {}\n".format(Path(filename).name, response["data"]["task_id"]))
    else:
        key = Path(filename).name
        key2taskId[key] = response["data"]["task_id"]
        with open("taskIds.txt", "w") as f:
            for key, taskId in key2taskId.items():
                f.write("{} {}\n".format(key, taskId))


if __name__ == "__main__":
    fire.Fire(main)
