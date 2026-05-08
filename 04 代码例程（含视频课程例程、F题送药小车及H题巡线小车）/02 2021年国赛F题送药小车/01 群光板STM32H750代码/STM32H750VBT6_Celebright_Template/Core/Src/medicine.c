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
#include "medicine.h"

/* USER CODE END Includes */


#define MoveDistance(cm) do { Set_Car_Control((cm) * 10, 0, 0); while(!car_control.oprate_done){osDelay(10);} } while(0)
#define TurnAngle(angle) do { Set_Car_Control_Absolute(0,0,(angle)); while(!car_control.oprate_done){osDelay(10);}} while(0)
#define bugLoop() do{Set_Car_Control(0,0,90); while(!car_control.oprate_done){osDelay(10); }} while(1)
#define TurnAngle(angle) do {Set_Car_Control(0,0, (angle));  while(!car_control.oprate_done){osDelay(10);}} while(0)

// #define LEFT 0x02    (Moved to header)
// #define RIGHT 0x04   (Moved to header)
// #define STRAIGHT 0x01 (Moved to header)

static void moveBack(CarState endState){
    switch (endState)
    {
    case end1L:
        TurnAngle(180);  // 从90度转到270度，相对转180度
        MoveDistance(55);
        TurnAngle(270);  // 从270度转到180度，相对转270度
        MoveDistance(75);
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end1R:
         TurnAngle(180);  // 从270度转到90度，相对转180度
         MoveDistance(55);
         TurnAngle(90);   // 从90度转到180度，相对转90度
         MoveDistance(75);
         TurnAngle(180);  // 从180度转到0度，相对转180度
         break;
    case end2L:
        TurnAngle(180);  // 从90度转到270度，相对转180度
        MoveDistance(55);
        TurnAngle(270);  // 从270度转到180度，相对转270度
        MoveDistance(165); // 25 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end2R:
        TurnAngle(180);  // 从270度转到90度，相对转180度
        MoveDistance(55);
        TurnAngle(90);   // 从90度转到180度，相对转90度
        MoveDistance(165); // 25 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end4LL:
        TurnAngle(180);  // 从180度转到0度，相对转180度
        MoveDistance(65);
        TurnAngle(270);  // 从0度转到270度，相对转270度
        MoveDistance(95); // 30 + 55
        TurnAngle(270);  // 从270度转到180度，相对转270度
        MoveDistance(255); // 25 + 90 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end4LR:
        TurnAngle(180);  // 从0度转到180度，相对转180度
        MoveDistance(65);
        TurnAngle(90);   // 从180度转到270度，相对转90度
        MoveDistance(95); // 30 + 55
        TurnAngle(270);  // 从270度转到180度，相对转270度
        MoveDistance(255); // 25 + 90 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end4RL:
        TurnAngle(180);  // 从0度转到180度，相对转180度
        MoveDistance(65);
        TurnAngle(270);  // 从180度转到90度，相对转270度
        MoveDistance(95); // 30 + 55
        TurnAngle(90);   // 从90度转到180度，相对转90度
        MoveDistance(255); // 25 + 90 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    case end4RR:
        TurnAngle(180);  // 从180度转到0度，相对转180度
        MoveDistance(65);
        TurnAngle(90);   // 从0度转到90度，相对转90度
        MoveDistance(95); // 30 + 55
        TurnAngle(90);   // 从90度转到180度，相对转90度
        MoveDistance(255); // 25 + 90 + 140
        TurnAngle(180);  // 从180度转到0度，相对转180度
        break;
    default:
        break;
    }
}

static CarState startMove(uint8_t direction){
    switch (direction)
    {
    case LEFT:
        MoveDistance(75);
        TurnAngle(90);   // 从0度转到90度，相对转90度
        MoveDistance(55);
        moveBack(end1L);
        return start;
        break;
    case RIGHT:
        MoveDistance(75);
        TurnAngle(270);  // 从0度转到270度，相对转270度
        MoveDistance(55);
        moveBack(end1R);
        return start;
        break;
    case STRAIGHT:
        MoveDistance(140);
        return secondCross;
        break;
    default:
        bugLoop();
        break;
    }
    return MED_ERROR;
}

static CarState secondMove(uint8_t direction){
    switch (direction)
    {
    case LEFT:
        MoveDistance(25);
        TurnAngle(90);   // 从0度转到90度，相对转90度
        MoveDistance(55);
        moveBack(end2L);
        return start;
        break;
    case RIGHT:
        MoveDistance(25);
        TurnAngle(270);  // 从0度转到270度，相对转270度
        MoveDistance(55);
        moveBack(end2R);
        return start;
        break;
    case STRAIGHT:
        MoveDistance(90);
        return thirdCross; 
        break;
    default:
        bugLoop();
        break;
    }
    return MED_ERROR;

}

static CarState thirdMove(uint8_t direction){
    switch (direction)
    {
    case LEFT:
        MoveDistance(25);
        TurnAngle(90);   // 从0度转到90度，相对转90度
        MoveDistance(55);
        return fourthLeftCross;
        break;
    case RIGHT:
        MoveDistance(25);
        TurnAngle(270);  // 从0度转到270度，相对转270度
        MoveDistance(55);
        return fourthRightCross;
        break;

    case STRAIGHT:
    default:
        bugLoop();
        break;
    }
    return MED_ERROR;
}

static CarState fourthLeftMove(uint8_t direction){
    switch (direction)
    {
    case LEFT:
        MoveDistance(30);
        TurnAngle(90);   // 从90度转到180度，相对转90度
        MoveDistance(65);
        moveBack(end4LL);
        return start;
        break;
    case RIGHT:
        MoveDistance(30);
        TurnAngle(270);  // 从90度转到0度，相对转270度
        MoveDistance(65);
        moveBack(end4LR);
        return start;
        break;

    case STRAIGHT:
    default:
        bugLoop();
        break;
    }
    return MED_ERROR;
}

static CarState fourthRightMove(uint8_t direction){
    switch (direction)
    {
    case LEFT:
        MoveDistance(30);
        TurnAngle(90);   // 从270度转到0度，相对转90度
        MoveDistance(65);
        moveBack(end4RL);
        return start;
        break;
    case RIGHT:
        MoveDistance(30);
        TurnAngle(270);  // 从270度转到180度，相对转270度
        MoveDistance(65);
        moveBack(end4RR);
        return start;
        break;

    case STRAIGHT:
    default:
        bugLoop();
        break;
    }
    return MED_ERROR;
}



int moveCtrl(uint8_t direction){
    static CarState state = start;

    switch (state)
    {
    case start:
        state = startMove(direction);
        break;

    case secondCross:
        state = secondMove(direction);
        break;

    case thirdCross:
        state = thirdMove(direction);
        break;
    
    case fourthLeftCross:
        state = fourthLeftMove(direction);
        break;

    case fourthRightCross:
        state = fourthRightMove(direction);
        break;
    
    case MED_ERROR:
    default:
        bugLoop();
        break;
    }


    switch (state)
    {
    case start:
        return 0;
        break;
    case secondCross:
        return 1;
        break;
    case thirdCross:
        return 2;
        break;
    case fourthLeftCross:
    case fourthRightCross:
        return 3;
    default:
        break;
    }
    bugLoop();
    return -1;
}
