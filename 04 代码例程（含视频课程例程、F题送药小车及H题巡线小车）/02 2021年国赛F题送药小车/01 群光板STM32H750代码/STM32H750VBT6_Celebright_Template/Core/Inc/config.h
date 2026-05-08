

#define 	USE_CAR_CONTROL 1
#define 	V_ANGLE_PID	1

/*数学常量*/
#define RAD_TO_DEGREE   57.29578018F     //弧度转角度
#define DEGREE_TO_RAD   0.01745329238F   //角度转弧度

/**************FreeRTOS设置******************** */
/**
 * @brief FreeRTOS各任务执行间隔时间,ms
 * 
 */
#define         TASK_ITV_CAR        10
#define         TASK_ITV_IMU        5
#define         TASK_ITV_UPLOAD     50


/*小车设置------------------------------------------*/

//电机个数,4个或2个,2个时使用前轮
#define         USE_4_MOTOR             1

//是否使用四倍频
#define         USE_4_TIMES_ENCODER     1
#define         V_DEGREE_FROM_IMU       1//用IMU

/*小车测速相关------------------------------------------*/

//每圈编码器数
#define         ENC_EVERY_CIRCLE        1061.268
//轮直径 mm
#define         WHEEL_DIR               47F
//轮周长 mm
#define         WHEEL_PERIMETER         148.722996F

//左右轮距的一半(用IMU测算)        !!单位mm!!
#define         FRAME_W_HALF            66.25F

//前后轮轴距的一半
#define         FRAME_L_HALF            55.85F


//圈速=实际速度/周长=编码器速度/每圈编码器数
//编码器速度/实际速度=每圈编码器数/周长         !!长度mm!!
//#define         V_REAL_TO_ENC           10.48929918F
#define         V_REAL_TO_ENC           (ENC_EVERY_CIRCLE/WHEEL_PERIMETER)

/*PID、PWM控制相关------------------------------------------*/

//电机目标编码器速度最大值,编码器单位/s
#define         MAX_V_ENC               (2*ENC_EVERY_CIRCLE)
//电机最大实际速度,mm/s
#define         MAX_V_REAL              MAX_V_ENC/V_REAL_TO_ENC
//最大角速度,degree/s
#define         MAX_V_ANGLE             100.0F     
//尺度变换,占空比的100%对应PID的1000,提高计算精度
#define         ZOOM_PID_TO_DUTY        0.001F

//电机输出最大PWM占空比
#define         MAX_MOTOR_DUTY          0.999F

//增量式PID增量限幅
#define         LIMIT_INC_LF            0.5F*MAX_MOTOR_DUTY/ZOOM_PID_TO_DUTY     /*单位:占空比1/1000*/
#define         LIMIT_INC_LR            0.5F*MAX_MOTOR_DUTY/ZOOM_PID_TO_DUTY     
#define         LIMIT_INC_RF            0.5F*MAX_MOTOR_DUTY/ZOOM_PID_TO_DUTY
#define         LIMIT_INC_RR            0.5F*MAX_MOTOR_DUTY/ZOOM_PID_TO_DUTY
#define         LIMIT_INC_POS           MAX_V_REAL*0.5F                              /*单位:mm/s,直线速度*/
#define         LIMIT_INC_SPIN          MAX_V_ANGLE                               /*单位:degree/s,角速度*/
#define         LIMIT_INC_V_ANGLE       0.5F*MAX_V_ANGLE*FRAME_W_HALF*DEGREE_TO_RAD                              /*单位:mm/s,角速度补偿速度*/
#define         LIMIT_INC_VITUAL_X      0.0F        /*单位百分比,线速度*/
#define         LIMIT_INC_VITUAL_Y      0.0F        /*单位百分比,角速度*/
//位置式PID限幅,PWM占空比100%对应PID的1000
#define         LIMIT_POS_LF            (MAX_MOTOR_DUTY*1000)
#define         LIMIT_POS_LR            (MAX_MOTOR_DUTY*1000)
#define         LIMIT_POS_RF            (MAX_MOTOR_DUTY*1000)
#define         LIMIT_POS_RR            (MAX_MOTOR_DUTY*1000)
#define         LIMIT_POS_POS           MAX_V_REAL 
#define         LIMIT_POS_SPIN          MAX_V_ANGLE
#define         LIMIT_POS_V_ANGLE       MAX_V_ANGLE*FRAME_W_HALF*DEGREE_TO_RAD
#define         LIMIT_POS_VITUAL_X      100.0F
#define         LIMIT_POS_VITUAL_Y      100.0F

//位置式PID积分限幅
#define         LIMIT_ITGR_MAX          1000000000.0F
#define         LIMIT_ITGR_LF           LIMIT_ITGR_MAX
#define         LIMIT_ITGR_LR           LIMIT_ITGR_MAX
#define         LIMIT_ITGR_RF           LIMIT_ITGR_MAX
#define         LIMIT_ITGR_RR           LIMIT_ITGR_MAX
#define         LIMIT_ITGR_POS          LIMIT_ITGR_MAX
#define         LIMIT_ITGR_SPIN         LIMIT_ITGR_MAX
#define         LIMIT_ITGR_V_ANGLE      LIMIT_ITGR_MAX
#define         LIMIT_ITGR_VITUAL_X     LIMIT_ITGR_MAX
#define         LIMIT_ITGR_VITUAL_Y     LIMIT_ITGR_MAX
/**
 * @brief PID参数
 * ****************************************************************************************************************************
 */
#define         P_LF            0.02F
#define         P_LR            0.02F
#define         P_RF            0.02F
#define         P_RR            0.02F
#define         P_POS           2.0F    //位置
#define         P_SPIN          2.5F    //原地旋转
#define         P_V_ANGLE       2.5F    //角速度
//#define         P_VITAUL_X      1.0F
//#define         P_VITAUL_Y      1.0F

#define         I_LF            0.01F
#define         I_LR            0.01F
#define         I_RF            0.01F
#define         I_RR            0.01F
#define         I_POS           0.01F
#define         I_SPIN          0.1F
#define         I_V_ANGLE       0.63F
//#define         I_VITAUL_X      0.0F
//#define         I_VITAUL_Y      0.0F

#define         D_LF            0.015F
#define         D_LR            0.015F
#define         D_RF            0.015F
#define         D_RR            0.015F
#define         D_POS           0.1F
#define         D_SPIN          0.05F
#define         D_V_ANGLE       0.01F
//#define         D_VITAUL_X      100.0F
//#define         D_VITAUL_Y      0.0F


