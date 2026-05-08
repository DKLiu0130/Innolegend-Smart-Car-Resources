import sensor,time

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)# 使用彩色模式，还常使用sensor.GRAYSCALE,灰度模式
sensor.set_framesize(sensor.QVGA)#320*240
sensor.skip_frames(time=2000)#缓冲2s，等待感光元件稳定
sensor.set_auto_gain(False)#关闭自动增益
sensor.set_auto_whitebal(False)#关闭自动白平衡
#sensor.set_hmirror(True)#水平翻转
#sensor.set_vflip(True)#垂直翻转

yellow_threshold=(44, 94, -15, 35, -7, 37)
clock=time.clock()
while(True):
    clock.tick()
    img = sensor.snapshot()
    blobs=img.find_blobs([yellow_threshold],pixels_threshold=1000,area_threshold=1000,merge=True)
    if blobs:
        main_blob=blobs[0]
        img.draw_rectangle(main_blob.rect(),color=(0,255,0))
        print("Blob Found!CX:",main_blob.cx(),"CY:",main_blob.cy())
