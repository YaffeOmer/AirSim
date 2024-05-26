import airsim
import socket
import pickle
import numpy as np

def initialize_drone():
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    client.takeoffAsync().join()
    # client.simPause(True)
    print("Drone initialized and taken off successfully")
    return client

def motor_controll (client,front_right_pwm, rear_left_pwm, front_left_pwm, rear_right_pwm, duration):
    # client.simPause(False)
    client.moveByMotorPWMsAsync(front_right_pwm, rear_left_pwm, front_left_pwm, rear_right_pwm, duration, vehicle_name='').join()

def read_imu_data (client):
    imu_data = client.getImuData(imu_name='', vehicle_name='')
    time_tag, a_x , a_y , a_z = imu_data.time_stamp, imu_data.linear_acceleration.x_val, imu_data.linear_acceleration.y_val, imu_data.linear_acceleration.z_val
    angular_Vel_x , angular_Vel_y , angular_Vel_z  = imu_data.angular_velocity.x_val, imu_data.angular_velocity.y_val, imu_data.angular_velocity.z_val
    return time_tag, a_x , a_y , a_z , angular_Vel_x , angular_Vel_y , angular_Vel_z

def capture_image (client, camera_location): 
    responses = client.simGetImages([airsim.ImageRequest(camera_location, airsim.ImageType.Scene, False, False)])
    return responses[0].image_data_uint8, responses[0].width, responses[0].height

# Create a socket to listen for commands
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen(1)

while True:
    print("Waiting for connection...")
    client_socket, addr = server_socket.accept()
    print("Connection from", addr)

    command = client_socket.recv(1024).decode()
    print("Received command:", command)

    if command == 'initialize':
        client = initialize_drone()

    elif command.startswith('motor_control'): 
        _, *params = command.split()
        params = list(map(float, params))
        motor_controll(client,*params)

    elif command == 'read_imu_data':
        imu_data = read_imu_data(client)
        imu_data_serialized = pickle.dumps(imu_data)
        client_socket.sendall(imu_data_serialized)

    elif command.startswith('render_image'):
        _, params = command.split()
        img_data = capture_image(client, params)
        img_serialized = pickle.dumps(img_data)
        client_socket.sendall(img_serialized)
    
    client_socket.close()