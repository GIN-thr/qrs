from machine import Pin, PWM
import time

# 初始化PWM对象，选择ESP32-C3上的一个支持PWM的引脚
# servo_pin = Pin(9)  # 将数字9替换为舵机连接的实际引脚
# pwm_servo = PWM(servo_pin, freq=50)  # 设置SG90舵机的PWM频率为50Hz

def servo_angle(pwm, angle):
    # 确保角度在0到180度之间
    if angle < 0 or angle > 180:
        raise ValueError("角度必须在0到180度之间。")
    # 计算PWM占空比，并设置舵机角度
    duty = int(((angle / 180) * (2.5 - 0.5) + 0.5) / 20 * 65535)
    pwm.duty_u16(duty)

# 将舵机初始角度设置为90度
current_angle = 90
servo_angle(pwm_servo, current_angle)


def rotate_left():
    # 计算新的角度，并防止角度小于0度
    current_angle = max(0, current_angle - 10)
    servo_angle(pwm_servo, current_angle)
    print(f"向左转至 {current_angle} 度。")

def rotate_right():
    # 计算新的角度，并防止角度大于180度
    current_angle = min(180, current_angle + 10)
    servo_angle(pwm_servo, current_angle)
    print(f"向右转至 {current_angle} 度。")
