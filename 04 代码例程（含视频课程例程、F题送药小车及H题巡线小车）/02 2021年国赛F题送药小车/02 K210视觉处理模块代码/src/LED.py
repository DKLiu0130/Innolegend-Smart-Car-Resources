
from fpioa_manager import fm
from Maix import GPIO
# LED的使用

led_pin_red			=		14
led_pin_green		=		13
led_pin_bule		=		12

# 注册 LED 引脚
fm.register(led_pin_red		, fm.fpioa.GPIO2, force = True)               # 配置 14 脚为 LED_R 强制注册
fm.register(led_pin_green	, fm.fpioa.GPIO1, force = True)               # 配置 13 脚为 LED_G 强制注册
fm.register(led_pin_bule	, fm.fpioa.GPIO0, force = True)               # 配置 12 脚为 LED_B 强制注册

# 创建 LED 对象
LED_R = GPIO(GPIO.GPIO2, GPIO.OUT, value = 1)                          # 创建 LED_R 对象
LED_G = GPIO(GPIO.GPIO1, GPIO.OUT, value = 1)                          # 创建 LED_G 对象
LED_B = GPIO(GPIO.GPIO0, GPIO.OUT, value = 1)                          # 创建 LED_B 对象

# LED控制函数
def LED_Control(led_flag):                                  # LED控制函数 根据传入 led_flag 点亮对应的灯 需要注意的是 0为点亮 1为熄灭
    if led_flag == 0:                                       # 传入参数为 0 所有灯打开
        LED_R.value(0)
        LED_G.value(0)
        LED_B.value(0)

    elif led_flag == 1:                                     # 传入参数为 1 红灯常亮
        LED_R.value(0)
        LED_G.value(1)
        LED_B.value(1)

    elif led_flag == 2:                                     # 传入参数为 2 绿灯常亮
        LED_R.value(1)
        LED_G.value(0)
        LED_B.value(1)

    elif led_flag == 3:                                     # 传入参数为 3 蓝灯常亮
        LED_R.value(1)
        LED_G.value(1)
        LED_B.value(0)

    elif led_flag == -1:                                    # 其他情况 全灭
        LED_R.value(1)
        LED_G.value(1)
        LED_B.value(1)
    else:
        LED_R.value(1)
        LED_G.value(1)
        LED_B.value(1)
