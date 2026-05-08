
#include <stdint.h>
#include <math.h>

#define true 1
#define false 0
#define PI (3.14159265358979323846f)

// 定义第三段臂的固定角度类型
typedef enum {
    U_VERTICAL = 0,    // 垂直向上
    U_DEGREE_45 = 1,    // 向上45度
    HORIZONTAL = 2,  // 水平
    D_DEGREE_45 = 3,    // 向下45度
    D_VERTICAL = 4,    // 垂直向下
} ArmThirdAngleType;


// 机械臂参数结构体
typedef struct {
    uint16_t H;                     // 底座高度
    uint16_t L1;                    // 第一段臂长度
    uint16_t L2;                    // 第二段臂长度
    uint16_t L3;                    // 第三段臂长度
    float angle;                    // 底座的旋转角度
    float theta1;                   // 第一段臂角度（弧度）
    float theta2;                   // 第二段臂角度（弧度）
    float theta3;                   // 第三段角度 (弧度)
    ArmThirdAngleType theta3_type;  // 第三段臂角度类型
    uint8_t isGripping;             // 表示当前夹子是否加紧
} RoboticArm;


// 末端执行器位置
typedef struct {
    uint16_t x;    // x坐标
    uint16_t y;    // y坐标
    uint16_t z;    // z坐标
} V_Position;

// 四个自由度的角度
typedef struct{
    float theta1;    // 第一段臂角度（弧度）
    float theta2;    // 第二段臂角度（弧度）
    float theta3;    // 第三段臂角度（弧度）
    float angle;     // 底座旋转角度（弧度）
} V_Angle;

typedef  struct{
    float x;
    float y;
    float z;
}Vf_Position;


uint8_t initRoboticArm(RoboticArm* arm,
                        uint16_t H, uint16_t L1, uint16_t L2, uint16_t L3,
                        float joint1, float joint2, float joint3, float joint4 ,ArmThirdAngleType theta3_type){

    if (arm == NULL || L1 <= 0 || L2 <= 0 || L3 <= 0) {
        return false;
    }

    arm->H              =       H;
    arm->L1             =       L1;
    arm->L2             =       L2;
    arm->L3             =       L3;
    arm->angle          =       joint4;
    arm->theta1         =       joint1;
    arm->theta2         =       joint2;
    arm->theta3         =       joint3;
    arm->theta3_type    =       theta3_type;
    arm->isGripping     =       false;
    return true;
}


uint8_t setArmType(RoboticArm* arm, ArmThirdAngleType type) {
    int typeid = (int)type;
    if (arm != NULL && (0 <= typeid && typeid <= 4)) {
        arm->theta3_type = type;
        return true;
    }else return false;
}


float getThirdArmAngle(ArmThirdAngleType type) {
    switch (type) {
        case U_VERTICAL:
            return PI / 2.0f;  // 90度 垂直向上
        case U_DEGREE_45:
            return PI / 4.0f;  // 45度 向上45度
        case HORIZONTAL:
            return 0.0f;       // 0度 水平
        case D_DEGREE_45:
            return -PI / 4.0f; // -45度 向下45度
        case D_VERTICAL:
            return -PI / 2.0f; // -90度 垂直向下
        default:
            return 0.0f;
    }
}


uint8_t inverseKinematics(RoboticArm* arm, const V_Position* target, V_Angle * angle){
    
    if (arm == NULL || target == NULL || angle == NULL) {
        return false;
    }

    if(target->z < 0){
        angle->theta1 = arm->theta1;
        angle->theta2 = arm->theta2;
        angle->theta3 = arm->theta3;
        angle->angle = arm->angle;
        return false;
    }

    // 首先计算底座旋转角度
    float baseAngle = atan2f(target->x, target->y);

    // 计算在x-z平面（旋转后的平面）上的投影距离
    float projectedDist = sqrtf((target->x * target->x + target->y * target->y));

    // 考虑第三段臂的偏移
    float AbsTheta3 = getThirdArmAngle(arm->theta3_type);
    float L3_x = arm->L3 * cosf(AbsTheta3);
    float L3_z = arm->L3 * sinf(AbsTheta3);

    // 计算第二段臂末端的目标位置
    float targetR = projectedDist - L3_x;
    float targetZ = target->z - L3_z - arm->H;

    // 调整目标高度，将底座高度考虑进去
    targetZ -= arm->H;

   
    float a0 = sqrtf(targetR * targetR + targetZ * targetZ);
    float Theta0 = atan2f(targetZ, targetR);

    float Theta1 = Theta0 + acosf((powf(targetR, 2) + powf(targetZ, 2) + powf(arm->L1, 2) - powf(arm->L2, 2))/ (2.0f * arm->L1 * a0));
    float Theta2 = Theta0 - Theta1 - acosf( (powf(targetR, 2) + powf(targetZ, 2) + powf(arm->L2, 2) - powf(arm->L1, 2)) / (2.0f * arm->L2 * a0) );
    float Theta3 = AbsTheta3 - (Theta1 + Theta2);

    angle->theta1 =  Theta1 - PI / 2;
    angle->theta2 = Theta2;
    angle->theta3 = Theta3;
    angle->angle = baseAngle;

    return true;
}
