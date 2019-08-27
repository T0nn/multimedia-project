from contentdetector import ContentDetector
import numpy as np
import time
import math
import wave
import brand
import os
import multiprocessing as mp

def replacead(sourcePath,newPath, targetPath, ad, ad_lens,width=480, height=270,frame_number=9000):
    with open(sourcePath, 'rb') as f:
        with open(targetPath, 'wb') as t:
            frame_size = width * height * 3
            i = 0
            newpath_index = 0
            while(i<frame_number):
                if i not in ad:
                    f.seek(i*frame_size)
                    t.write(f.read(frame_size))
                    i += 1
                else:
                    with open(newPath[newpath_index], 'rb') as n:
                        t.write(n.read())
                    i += ad_lens[newpath_index]
                    newpath_index += 1

def replacesound(sourcePath,newPath, targetPath, ad, ad_lens, frame_number):
    with wave.open(sourcePath,"rb") as f:
        channels = f.getnchannels()
        for_mat = f.getsampwidth()
        rate = f.getframerate()
        chunk = 1024
        with wave.open(targetPath,"wb") as w:
            w.setnchannels(channels)
            w.setsampwidth(for_mat)
            w.setframerate(rate)
            i = 0
            newpath_index = 0
            while (i < frame_number):
                if i not in ad:
                    f.setpos(i * chunk)
                    w.writeframes(f.readframes(chunk))
                    i += 1
                else:
                    with wave.open(newPath[newpath_index], 'rb') as n:
                        w.writeframes(n.readframes(n.getnframes()))
                    i += int(ad_lens[newpath_index])
                    newpath_index += 1

def appendresult(result):
    t = result.data.reshape((height * width, -1))
    t = t.transpose()
    temp[result.index] = t.reshape(1, -1)
    print("Current frame :", result.index)


if __name__ == "__main__":
    ##intitialize##
    # video_source = "./data_test2.rgb"
    # video_target = "./result2.rgb"
    # video_new = ["./nfl_Ad_15s.rgb", "./mcd_Ad_15s.rgb"]
    # audio_source = "./data_test2.wav"
    # audio_target = "./result2.wav"
    # audio_new = ["./nfl_Ad_15s.wav", "./mcd_Ad_15s.wav"]

    # ad_logo = ["./dataset/Brand Images/subway_logo.rgb", "./dataset/Brand Images/starbucks_logo.rgb"]
    # video_source = "./dataset/Videos/data_test1.rgb"
    # video_target = "./result.rgb"
    # video_new = ["./dataset/Ads/Subway_Ad_15s.rgb", "./dataset/Ads/Starbucks_Ad_15s.rgb"]
    # audio_source = "./dataset/Videos/data_test1.wav"
    # audio_target = "./result.wav"
    # audio_new = ["./dataset/Ads/Subway_Ad_15s.wav", "./dataset/Ads/Starbucks_Ad_15s.wav"]

    ad_logo = ["./dataset3/dataset3/Brand Images/ae_logo.rgb", "./dataset3/dataset3/Brand Images/hrc_logo.rgb"]
    video_source = "./dataset3/dataset3/Videos/data_test3.rgb"
    video_target = "./result.rgb"
    video_new = ["./dataset3/dataset3/Ads/ae_ad_15s.rgb", "./dataset3/dataset3/Ads/hrc_ad_15s.rgb"]
    audio_source = "./dataset3/dataset3/Videos/data_test3.wav"
    audio_target = "./result.wav"
    audio_new = ["./dataset3/dataset3/Ads/ae_ad_15s.wav", "./dataset3/dataset3/Ads/hrc_ad_15s.wav"]

    cut = [0]
    ad_video = []
    ad_video_lens = []
    ad_audio = []
    ad_audio_lens = []
    c_d = ContentDetector()
    height = 270
    width = 480
    channel = 3
    size = height * width * channel

    trainKP, trainDesc = brand.siftdetector(ad_logo)

    ## get the length of video ##
    with open(video_source, "rb") as f:
        num = 0
        data = f.read(size)
        while data:
            num += 1
            data = f.read(size)
        print("video size :", num)
        num_frame = num

    ## get the length of audio##
    with wave.open(audio_source, "rb") as f:
        chunk = 1024
        audio_num = int(f.getnframes() / chunk)
        print("audio size :", audio_num)

    ## read the image to buffer and cut the scene ##
    time1 = time.time()
    temp = np.zeros((num_frame, height * width * channel), dtype=np.uint8)
    img = np.zeros((num_frame, height, width, channel), dtype=np.uint8)
    with open(video_source, "rb") as f:
        for i in range(num_frame):
            b = f.read(size)
            a = np.frombuffer(b, dtype=np.uint8)
            a = a.reshape((channel, -1))
            a = a.transpose()
            QueryImgRGB = a.reshape((height, width, channel))
            img[i] = QueryImgRGB
            c_d.process_frame(i, img[i])
            # QueryImgRGB = brand.brandmatch(i, trainKP, trainDesc, QueryImgRGB)
            # t = QueryImgRGB.reshape((height * width, -1))
            # t = t.transpose()
            # temp[i] = t.reshape(1, -1)
            print("Current frame :", i)
    pool = mp.Pool(processes=4)
    for i in range(img.shape[0]):
        pool.apply_async(brand.brandmatch, args=(i, trainKP, trainDesc, img[i],), callback=appendresult)
    pool.close()
    pool.join()

    temp.tofile("./result.tmp")
    del temp

    for i in range(len(c_d.cut_list)):
        cut.append(c_d.cut_list[i])
    cut.append(num_frame - 1)
    is_ad = [False] * len(cut)
    print("Frame for cut :", cut)

    ## recognize the ads ##
    #threshhold = 1
    for i in range(1, len(cut)):
        # if cut[i] - cut[i-1] < 300:
        #     is_ad[i-1] = True
        # elif cut[i] - cut[i-1] < 600:
        #     ad_detector = ContentDetector(threshold=50, min_scene_len=30)
        #     for j in range(cut[i-1], cut[i]):
        #         ad_detector.process_frame(j, img[j])
        #     print("Number of scene changes in a shot :", len(ad_detector.cut_list))
        #     if len(ad_detector.cut_list) > threshhold:
        #         is_ad[i-1] = True
        #     del ad_detector
        if cut[i] - cut[i - 1] < 600:
            is_ad[i - 1] = True



    # merge adjacent ads##
    k1 = 0
    while k1 < len(is_ad):
        if is_ad[k1]:
            k2 = k1
            while is_ad[k2]:
                k2 += 1
            ad_video.append(cut[k1])
            ad_video_lens.append(cut[k2] - cut[k1])
            ad_audio.append(int(cut[k1] * audio_num / num_frame))
            ad_audio_lens.append(int((cut[k2] - cut[k1]) * audio_num / num_frame))
            k1 = k2
        else:
            k1 += 1

    print("Video ad start frame :", ad_video)
    print("Video ad frame length :", ad_video_lens)
    print("Audio ad start frame :", ad_audio)
    print("Audio ad frame length :", ad_audio_lens)

    ###replace ad ###
    replacead("./result.tmp", video_new, video_target, ad_video, ad_video_lens)
    replacesound(audio_source, audio_new, audio_target, ad_audio, ad_audio_lens, audio_num)
    time2 = time.time()
    print("Total time :", time2 - time1)

    ##print the time where the ads exist##
    cut_time = []
    ad_time = []
    for i in range(len(cut)):
        cut[i] = (int)(cut[i] / 30)
        min = math.floor(cut[i] / 60)
        second = cut[i] % 60
        t = str(min) + ':' + str(second)
        cut_time.append(t)
    for i in range(len(ad_video)):
        ad_video[i] = (int)(ad_video[i] / 30)
        min = math.floor(ad_video[i] / 60)
        second = ad_video[i] % 60
        t = str(min) + ':' + str(second)
        ad_time.append(t)
    print("Cut time:", cut_time)
    print("Ad time :", ad_time)

    os.remove("./result.tmp")
