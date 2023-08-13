import paramiko
import time, os
import select

# 定义SSH连接信息
gauss_hostname = '202.120.38.69'
gauss_port = 5566
gauss_username = 'gyh17'
gauss_password = 'Sp1ch!ab'
fourier_hostname='fourier'
fourier_password='Sp1ch!ab'


def wait_for_response(length=1):
    time.sleep(3)
    ready = select.select([channel], [], [], 30.0)
    if ready[0]:
    # 如果有数据到来，则读取数据
        output = channel.recv(1024*length)
        return output
    else:
    # 如果没有数据到来，则提示超时
        print("Timeout waiting for data")


# 建立SSH连接
ssh_gauss = paramiko.SSHClient()
ssh_gauss.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_gauss.connect(gauss_hostname, gauss_port, gauss_username, gauss_password)

# 使用SSH连接执行命令
stdin, stdout, stderr = ssh_gauss.exec_command('ls -l')
print(stdout.read().decode('gb18030'))



############################connect to fourier##############################

# 使用SSH连接执行命令
channel = ssh_gauss.invoke_shell()  # 建立交互式会话
channel.send('ssh fourier\n')  # 连接到fourier
#output = channel.recv(1024)  # 读取命令输出
#print(output.decode())
time.sleep(10)
print(wait_for_response().decode())

channel.send(fourier_password+'\n')
#output = channel.recv(1024)  # 读取命令输出
#print(output.decode())
time.sleep(5)
print(wait_for_response().decode())


channel.send('nvidia-smi\n')  # 在fourier上执行nvidia-smi命令
time.sleep(3)
#output = channel.recv(1024*10)  # 读取命令输出
#print(output.decode())
print(wait_for_response(10).decode())

channel.send('ls -l\n')
print(wait_for_response().decode())
#time.sleep(3)
#output = channel.recv(1024)
#print(output.decode())
channel.send('conda activate 3d\n')
print(wait_for_response().decode())

channel.send('cd /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved\n')
print(wait_for_response().decode())

channel.send('ls\n')
print(wait_for_response().decode())

channel.send('python /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/scripts/prepare_testing_files.py\n')
time.sleep(8)
print(wait_for_response(10).decode())

channel.send('bash /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/experiments/demo_vox.sh\n')
time.sleep(20)
print(wait_for_response(20).decode())
###########################end of connection###################################
# 建立SFTP连接
sftp = ssh_gauss.open_sftp()

# 上传文件
#local_file_path = '/Users/yixinzhang/visual_sys/ssh_file/syn_audio.mp3'
#remote_file_path = '/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file/syn_audio.mp3'
#sftp.put(local_file_path, remote_file_path)

# 下载文件
local_result_path = '/Users/yixinzhang/visual_sys/ssh_result/avconcat.mp4'
remote_result_path = '/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/results/id_image_source_pose_pose_source_audio_syn_audio/avconcat.mp4'
sftp.get(remote_result_path, local_result_path)

# 关闭SFTP连接
sftp.close()

# 关闭SSH连接
ssh_gauss.close()