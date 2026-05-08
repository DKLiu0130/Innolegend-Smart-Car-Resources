/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "IMU.h"
#include "motor.h"
#include "tim.h"
#include "spi.h"
#include "quadspi.h"
#include "keyboard.h"
#include "config.h"
#include "car_attitude.h"
#include "car_control.h"
#include <../../SCSLib/SCServo.h>
#include "holder2D.h"
#include "roboticArm.h"
#include "ARobot.h"
#include "uart_fifo.h"
#include "oled_spi_V0.2.h"
#include "MusicPlayer.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
typedef StaticTask_t osStaticThreadDef_t;
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */
extern float motion6[7];
extern float ypr[3];          // yaw pitch roll
extern int math_pl;
QueueHandle_t uart3_frame_queue;
QueueHandle_t uart4_frame_queue;
QueueHandle_t uart5_frame_queue;
TaskHandle_t xMotionTaskHandle = NULL;


/* USER CODE END Variables */
/* Definitions for LEDBlink */
osThreadId_t LEDBlinkHandle;
uint32_t LEDBlinkBuffer[ 128 ];
osStaticThreadDef_t LEDBlinkControlBlock;
const osThreadAttr_t LEDBlink_attributes = {
  .name = "LEDBlink",
  .cb_mem = &LEDBlinkControlBlock,
  .cb_size = sizeof(LEDBlinkControlBlock),
  .stack_mem = &LEDBlinkBuffer[0],
  .stack_size = sizeof(LEDBlinkBuffer),
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* Definitions for Broadcast */
osThreadId_t BroadcastHandle;
uint32_t BroadcastBuffer[ 256 ];
osStaticThreadDef_t BroadcastControlBlock;
const osThreadAttr_t Broadcast_attributes = {
  .name = "Broadcast",
  .cb_mem = &BroadcastControlBlock,
  .cb_size = sizeof(BroadcastControlBlock),
  .stack_mem = &BroadcastBuffer[0],
  .stack_size = sizeof(BroadcastBuffer),
  .priority = (osPriority_t) osPriorityNormal1,
};
/* Definitions for Uart4Handle */
osThreadId_t Uart4HandleHandle;
uint32_t UartHandleBuffer[ 256 ];
osStaticThreadDef_t UartHandleControlBlock;
const osThreadAttr_t Uart4Handle_attributes = {
  .name = "Uart4Handle",
  .cb_mem = &UartHandleControlBlock,
  .cb_size = sizeof(UartHandleControlBlock),
  .stack_mem = &UartHandleBuffer[0],
  .stack_size = sizeof(UartHandleBuffer),
  .priority = (osPriority_t) osPriorityNormal7,
};
/* Definitions for _9axisService */
osThreadId_t _9axisServiceHandle;
uint32_t _9axisServiceBuffer[ 128 ];
osStaticThreadDef_t _9axisServiceControlBlock;
const osThreadAttr_t _9axisService_attributes = {
  .name = "_9axisService",
  .cb_mem = &_9axisServiceControlBlock,
  .cb_size = sizeof(_9axisServiceControlBlock),
  .stack_mem = &_9axisServiceBuffer[0],
  .stack_size = sizeof(_9axisServiceBuffer),
  .priority = (osPriority_t) osPriorityNormal3,
};
/* Definitions for CarAttitude */
osThreadId_t CarAttitudeHandle;
uint32_t CarAttitudeBuffer[ 128 ];
osStaticThreadDef_t CarAttitudeControlBlock;
const osThreadAttr_t CarAttitude_attributes = {
  .name = "CarAttitude",
  .cb_mem = &CarAttitudeControlBlock,
  .cb_size = sizeof(CarAttitudeControlBlock),
  .stack_mem = &CarAttitudeBuffer[0],
  .stack_size = sizeof(CarAttitudeBuffer),
  .priority = (osPriority_t) osPriorityNormal5,
};
/* Definitions for Key */
osThreadId_t KeyHandle;
uint32_t KeyBuffer[ 128 ];
osStaticThreadDef_t KeyControlBlock;
const osThreadAttr_t Key_attributes = {
  .name = "Key",
  .cb_mem = &KeyControlBlock,
  .cb_size = sizeof(KeyControlBlock),
  .stack_mem = &KeyBuffer[0],
  .stack_size = sizeof(KeyBuffer),
  .priority = (osPriority_t) osPriorityNormal6,
};
/* Definitions for Buzzer */
osThreadId_t BuzzerHandle;
uint32_t BuzzerBuffer[ 128 ];
osStaticThreadDef_t BuzzerControlBlock;
const osThreadAttr_t Buzzer_attributes = {
  .name = "Buzzer",
  .cb_mem = &BuzzerControlBlock,
  .cb_size = sizeof(BuzzerControlBlock),
  .stack_mem = &BuzzerBuffer[0],
  .stack_size = sizeof(BuzzerBuffer),
  .priority = (osPriority_t) osPriorityNormal1,
};
/* Definitions for Screen_LCD */
osThreadId_t Screen_LCDHandle;
uint32_t Screen_LCDBuffer[ 128 ];
osStaticThreadDef_t Screen_LCDControlBlock;
const osThreadAttr_t Screen_LCD_attributes = {
  .name = "Screen_LCD",
  .cb_mem = &Screen_LCDControlBlock,
  .cb_size = sizeof(Screen_LCDControlBlock),
  .stack_mem = &Screen_LCDBuffer[0],
  .stack_size = sizeof(Screen_LCDBuffer),
  .priority = (osPriority_t) osPriorityNormal1,
};
/* Definitions for todo */
osThreadId_t todoHandle;
uint32_t todoBuffer[ 1024 ];
osStaticThreadDef_t todoControlBlock;
const osThreadAttr_t todo_attributes = {
  .name = "todo",
  .cb_mem = &todoControlBlock,
  .cb_size = sizeof(todoControlBlock),
  .stack_mem = &todoBuffer[0],
  .stack_size = sizeof(todoBuffer),
  .priority = (osPriority_t) osPriorityNormal1,
};
/* Definitions for Uart3Handle */
osThreadId_t Uart3HandleHandle;
uint32_t Uart3HandleBuffer[ 256 ];
osStaticThreadDef_t Uart3HandleControlBlock;
const osThreadAttr_t Uart3Handle_attributes = {
  .name = "Uart3Handle",
  .cb_mem = &Uart3HandleControlBlock,
  .cb_size = sizeof(Uart3HandleControlBlock),
  .stack_mem = &Uart3HandleBuffer[0],
  .stack_size = sizeof(Uart3HandleBuffer),
  .priority = (osPriority_t) osPriorityNormal7,
};
/* Definitions for MedicineDelivery */
osThreadId_t MedicineDeliveryHandle;
uint32_t MedicineDeliveryBuffer[ 256 ];
osStaticThreadDef_t MedicineDeliveryControlBlock;
const osThreadAttr_t MedicineDelivery_attributes = {
  .name = "MedicineDelivery",
  .cb_mem = &MedicineDeliveryControlBlock,
  .cb_size = sizeof(MedicineDeliveryControlBlock),
  .stack_mem = &MedicineDeliveryBuffer[0],
  .stack_size = sizeof(MedicineDeliveryBuffer),
  .priority = (osPriority_t) osPriorityNormal7,
};
/* Definitions for queue_key */
osMessageQueueId_t queue_keyHandle;
const osMessageQueueAttr_t queue_key_attributes = {
  .name = "queue_key"
};
/* Definitions for semphr_buzzer_trigger */
osSemaphoreId_t semphr_buzzer_triggerHandle;
const osSemaphoreAttr_t semphr_buzzer_trigger_attributes = {
  .name = "semphr_buzzer_trigger"
};
/* Definitions for semphr_uart_receive */
osSemaphoreId_t semphr_uart_receiveHandle;
const osSemaphoreAttr_t semphr_uart_receive_attributes = {
  .name = "semphr_uart_receive"
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */
void Task_APP();
void send_position(uint8_t current_position);
void move_back(void);
void move_ctrl(uint8_t direction);
/* USER CODE END FunctionPrototypes */

void Task_LEDBlink(void *argument);
void Task_Broadcast(void *argument);
void Task_Uart4Handle(void *argument);
void Task_9axisService(void *argument);
void Task_CarAttitude(void *argument);
void Task_Key(void *argument);
void Task_Buzzer(void *argument);
void Task_Screen(void *argument);
void Task_todo(void *argument);
void TaskUart3Handle(void *argument);
void Task_MedicineDelivery(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* Create the semaphores(s) */
  /* creation of semphr_buzzer_trigger */
  semphr_buzzer_triggerHandle = osSemaphoreNew(1, 1, &semphr_buzzer_trigger_attributes);

  /* creation of semphr_uart_receive */
  semphr_uart_receiveHandle = osSemaphoreNew(16, 0, &semphr_uart_receive_attributes);

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* Create the queue(s) */
  /* creation of queue_key */
  queue_keyHandle = osMessageQueueNew (1, sizeof(char), &queue_key_attributes);

  /* USER CODE BEGIN RTOS_QUEUES */
	uart3_frame_queue = xQueueCreate(5, UART_FRAME_MAX_LEN); // 最多缓存5帧，每帧64字节
	uart4_frame_queue = xQueueCreate(5, UART_FRAME_MAX_LEN); // 最多缓存5帧，每帧64字节
	uart5_frame_queue = xQueueCreate(5, UART_FRAME_MAX_LEN); // 最多缓存5帧，每帧64字节
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of LEDBlink */
  LEDBlinkHandle = osThreadNew(Task_LEDBlink, NULL, &LEDBlink_attributes);

  /* creation of Broadcast */
  BroadcastHandle = osThreadNew(Task_Broadcast, NULL, &Broadcast_attributes);

  /* creation of Uart4Handle */
  Uart4HandleHandle = osThreadNew(Task_Uart4Handle, NULL, &Uart4Handle_attributes);

  /* creation of _9axisService */
  _9axisServiceHandle = osThreadNew(Task_9axisService, NULL, &_9axisService_attributes);

  /* creation of CarAttitude */
  CarAttitudeHandle = osThreadNew(Task_CarAttitude, NULL, &CarAttitude_attributes);

  /* creation of Key */
  KeyHandle = osThreadNew(Task_Key, NULL, &Key_attributes);

  /* creation of Buzzer */
  BuzzerHandle = osThreadNew(Task_Buzzer, NULL, &Buzzer_attributes);

  /* creation of Screen_LCD */
  Screen_LCDHandle = osThreadNew(Task_Screen, NULL, &Screen_LCD_attributes);

  /* creation of todo */
  todoHandle = osThreadNew(Task_todo, NULL, &todo_attributes);

  /* creation of Uart3Handle */
  Uart3HandleHandle = osThreadNew(TaskUart3Handle, NULL, &Uart3Handle_attributes);

  /* creation of MedicineDelivery */
  MedicineDeliveryHandle = osThreadNew(Task_MedicineDelivery, NULL, &MedicineDelivery_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
	Key_StartScanTask();
	//xTaskCreate(Task_APP,"Test",512,NULL,(osPriority_t) osPriorityNormal5,NULL);
	//xTaskCreate(Task_exam_24H,"24_H",512,NULL,(osPriority_t) osPriorityNormal5,NULL);
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_Task_LEDBlink */
/**
  * @brief  Function implementing the LEDBlink thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_Task_LEDBlink */
void Task_LEDBlink(void *argument)
{
  /* USER CODE BEGIN Task_LEDBlink */
  /* Infinite loop */
  for(;;)
  { 
		HAL_GPIO_TogglePin(LED0_GPIO_Port, LED0_Pin);
    osDelay(1000);
  }
  /* USER CODE END Task_LEDBlink */
}

/* USER CODE BEGIN Header_Task_Broadcast */
/**
* @brief Function implementing the Broadcast thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_Broadcast */
void Task_Broadcast(void *argument)
{
  /* USER CODE BEGIN Task_Broadcast */
  /* Infinite loop */
  for(;;)
  {
		char buf[64];
		
		char* msg = "HelloFromStation\n";
		HAL_UART_Transmit(&huart4, (uint8_t*)msg, strlen(msg), 100);//Send To BT

    osDelay(50);
  }
  /* USER CODE END Task_Broadcast */
}

/* USER CODE BEGIN Header_Task_Uart4Handle */
/**
* @brief Function implementing the Uart4Handle thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_Uart4Handle */
void Task_Uart4Handle(void *argument)
{
  /* USER CODE BEGIN Task_Uart4Handle */
  char frame[UART_FRAME_MAX_LEN];



    /* Infinite loop */
    for(;;)
    {
        memset(frame, 0, sizeof(frame));
        // 从队列拿到一帧数据（由中断回调送入队列）
        if (xQueueReceive(uart4_frame_queue, frame, portMAX_DELAY) == pdPASS) {
						// Todo:解析帧数据

        }
    }
  /* USER CODE END Task_Uart4Handle */
}

/* USER CODE BEGIN Header_Task_9axisService */
/**
* @brief Function implementing the _9axisService thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_9axisService */
void Task_9axisService(void *argument)
{
  /* USER CODE BEGIN Task_9axisService */
	TickType_t xLastWakeTime;
	const TickType_t xFrequency = TASK_ITV_IMU;
	xLastWakeTime = xTaskGetTickCount();
  /* Infinite loop */
  for(;;)
  {
		vTaskDelayUntil( &xLastWakeTime, xFrequency );
	  uint8_t data[8] = {1,2,3,4,5,6,7,8};
	  IMU_getYawPitchRoll(ypr);
		IMU_TT_getgyro(motion6);
		Car_Attitude_Update_Input();
		math_pl++;	
  }
  /* USER CODE END Task_9axisService */
}

/* USER CODE BEGIN Header_Task_CarAttitude */
/**
* @brief Function implementing the CarAttitude thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_CarAttitude */
void Task_CarAttitude(void *argument)
{
  /* USER CODE BEGIN Task_CarAttitude */
	TickType_t xLastWakeTime;
	const TickType_t xFrequency = TASK_ITV_CAR;
	xLastWakeTime = xTaskGetTickCount();
  /* Infinite loop */
  for(;;)
  {
		vTaskDelayUntil( &xLastWakeTime, xFrequency );
		Tim_Update_Enc_Speed();//更新编码器速度
 	  Motor_Update_Input_All();
		Car_Attitude_Update_Input();
		Car_Control_Update_Input();
		Car_Control_Update_Output();
		Car_Attitude_Update_Output();
 		Motor_Update_Output_All();				
  }
  /* USER CODE END Task_CarAttitude */
}

/* USER CODE BEGIN Header_Task_Key */
/**
* @brief Function implementing the Key thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_Key */
void Task_Key(void *argument)
{
  /* USER CODE BEGIN Task_Key */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END Task_Key */
}

/* USER CODE BEGIN Header_Task_Buzzer */
/**
* @brief Function implementing the Buzzer thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_Buzzer */
void Task_Buzzer(void *argument)
{
  /* USER CODE BEGIN Task_Buzzer */
  /* Infinite loop */
  for(;;)
  {
    //PlayNote(M1, 100); // 播放音符 M1，持续时间 100ms
    osDelay(1);
  }
  /* USER CODE END Task_Buzzer */
}

/* USER CODE BEGIN Header_Task_Screen */
/**
* @brief Function implementing the Screen thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_Screen */
void Task_Screen(void *argument)
{
  /* USER CODE BEGIN Task_Screen */
  /* Infinite loop */
  for(;;)
  {
		OLED_ShowString(0, 0, "Hello World!");
    osDelay(100);
  }
  /* USER CODE END Task_Screen */
}

/* USER CODE BEGIN Header_Task_todo */
/**
* @brief Function implementing the todo thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Task_todo */
void Task_todo(void *argument)
{
  /* USER CODE BEGIN Task_todo */

	for(;;)
	{
    // 这里可以添加一些待办事项的处理逻辑
			osDelay(50);
	}
  /* USER CODE END Task_todo */
}

/* USER CODE BEGIN Header_TaskUart3Handle */
/**
* @brief Function implementing the Uart3Handle thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_TaskUart3Handle */
void TaskUart3Handle(void *argument)
{
  /* USER CODE BEGIN TaskUart3Handle */
  char frame[UART_FRAME_MAX_LEN];


    /* Infinite loop */
    for(;;)
    {
        memset(frame, 0, sizeof(frame));
        // 从队列拿到一帧数据（由中断回调送入队列）
        if (xQueueReceive(uart3_frame_queue, frame, portMAX_DELAY) == pdPASS) {
            // 处理接收到的帧数据
        }
    }
  /* USER CODE END TaskUart3Handle */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */


void Task_APP()
{		
		uart_frame_rx_init();
    // 初始化机械臂
    //setup_roboticArm();
    // 初始化机械臂位置
    //init_ArmForRTOS();
    // 移动机械臂到指定位置
    //moveArmForRTOS(150, 200, 50);
		vTaskDelete(NULL);//删除当前任务
}


#include "medicine.h"

void send_position(uint8_t current_position)
{
    // 构造位置信息帧：FE + 位置字节 + FD
    uint8_t position_frame[3];
    position_frame[0] = 0xFE;  // 帧头
    
    // 前4位固定为0000，后4位是位置编码
    // 0号路口: 0001, 1号路口: 0010, 2号路口: 0100, 3号路口: 1000
    uint8_t position_code;
    switch (current_position) {
        case 0:
            position_code = 0x01;  // 0001
            break;
        case 1:
            position_code = 0x02;  // 0010
            break;
        case 2:
            position_code = 0x04;  // 0100
            break;
        case 3:
            position_code = 0x08;  // 1000
            break;
        default:
            position_code = 0x00;  // 无效位置
            break;
    }
    
    position_frame[1] = (0x00 << 4) | position_code;  // 前4位0000，后4位位置
    position_frame[2] = 0xFD;  // 帧尾
    
    // 发送位置信息给摄像头
    HAL_UART_Transmit(&huart5, position_frame, 3, 100);
}


void Task_MedicineDelivery(void *argument)
{
  uart_frame_rx_init();
  /* USER CODE BEGIN Task_MedicineDelivery */
  uint8_t frame[UART_FRAME_MAX_LEN];
  uint8_t direction;
  const TickType_t timeout_ticks = pdMS_TO_TICKS(20000); // 20秒超时
  
  // 发送初始位置
  send_position(0);
  
  for(;;)
  {
    memset(frame, 0, sizeof(frame));
    
    // 尝试从队列接收数据，设置5秒超时
    if (xQueueReceive(uart5_frame_queue, frame, timeout_ticks) == pdPASS) {
      // 收到数据，解析并执行
      if (frame[0] == 0xFE && frame[2] == 0xFD) {  // 检查帧头帧尾
        uint8_t data_byte = frame[1];  // 中间的数据字节
        
        // 解析后3位，获取转向指令
        direction = data_byte & 0x07;  // 取后3位
      } else {
        // 帧格式错误，使用默认左转
        direction = 0x04;
      }
    } else {
      // 5秒内没有收到数据，使用默认左转
      direction = 0x04;
    }
    
    // 执行移动控制
    int position = moveCtrl(direction);
    send_position(position);
    
  }
  /* USER CODE END Task_MedicineDelivery */ 
}
/* USER CODE END Application */

