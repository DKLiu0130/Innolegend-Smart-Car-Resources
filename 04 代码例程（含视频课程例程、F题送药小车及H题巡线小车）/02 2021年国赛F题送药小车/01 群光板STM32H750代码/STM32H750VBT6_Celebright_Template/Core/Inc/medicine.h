
#ifndef __MEDICINE_H
#define __MEDICINE_H

#include "main.h"

// 方向指令定义
#define LEFT 0x02
#define RIGHT 0x04
#define STRAIGHT 0x01

typedef enum CarState{
    start,
    firstCross,
    secondCross,
    thirdCross,       
    fourthLeftCross,
    fourthRightCross,
    end4LL,
    end4LR,
    end4RR,
    end4RL,           
    end1L,
    end1R,
    end2L,
    end2R,
    MED_ERROR
} CarState;

/**
 * @brief 移动控制状态机
 * @param direction 方向指令 (LEFT/RIGHT/STRAIGHT)
 * @return CarState 下一个状态
 */
int moveCtrl(uint8_t direction);

#endif