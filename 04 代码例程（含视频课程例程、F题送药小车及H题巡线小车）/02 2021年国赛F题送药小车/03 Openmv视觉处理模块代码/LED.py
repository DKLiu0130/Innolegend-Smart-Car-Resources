from pyb import LED

# OpenMV Cam H7 Plus的LED配置
# 根据OpenMV Cam H7 Plus的引脚图，LED引脚如下：
# LED1 - 红色
# LED2 - 绿色  
# LED3 - 蓝色
# LED4 - 红外

# 创建LED对象 - OpenMV使用pyb.LED
led_red = LED(1)    # 红色LED
led_green = LED(2)  # 绿色LED
led_blue = LED(3)   # 蓝色LED

# LED控制函数
def LED_Control(led_flag):
    """
    LED控制函数，根据传入的led_flag点亮对应的灯
    注意：OpenMV的LED是低电平点亮，高电平熄灭
    
    :param led_flag: LED控制标志
        0: 所有灯打开
        1: 红灯常亮
        2: 绿灯常亮
        3: 蓝灯常亮
        -1或其他: 全灭
    """
    if led_flag == 0:  # 传入参数为 0，所有灯打开
        led_red.on()
        led_green.on()
        led_blue.on()

    elif led_flag == 1:  # 传入参数为 1，红灯常亮
        led_red.on()
        led_green.off()
        led_blue.off()

    elif led_flag == 2:  # 传入参数为 2，绿灯常亮
        led_red.off()
        led_green.on()
        led_blue.off()

    elif led_flag == 3:  # 传入参数为 3，蓝灯常亮
        led_red.off()
        led_green.off()
        led_blue.on()

    elif led_flag == -1:  # 其他情况，全灭
        led_red.off()
        led_green.off()
        led_blue.off()
    else:
        led_red.off()
        led_green.off()
        led_blue.off()
