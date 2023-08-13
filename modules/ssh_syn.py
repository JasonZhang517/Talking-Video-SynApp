import paramiko

#username="gyh17"
#password="Sp1ch!ab"

local_file_path="/Users/yixinzhang/visual_sys/ssh_file/syn_audio.mp3"
remote_file_path="/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file"

remote_result_path="/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_result/avconcat.mp4"
local_result_path="/Users/yixinzhang/visual_sys/ssh_result"

# 连接远程主机
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='202.120.38.69', port=5566, username='gyh17', password='Sp1ch!ab')

# 打开交互式shell并执行命令
#shell = ssh.invoke_shell()
#shell.send('ssh fourier\n')
#while not shell.recv_ready():
#    pass
#shell.recv(1024)
#shell.send('Sp1ch!ab\n')

# 连接目标机器
#ssh.exec_command('hostname') # 执行一个命令，以检查是否已经成功连接到目标机器

# 使用sftp传输文件
#sftp = ssh.open_sftp()
#sftp.put(local_file_path, remote_file_path)
#with sftp.open(remote_file_path, 'r+') as f:
#    content = f.read().decode('utf-8')
#    content = content.replace('parser.add_argument(\'--src_audio_path\', default=\'/mnt/xlancefs/home/gyh17/3D_face/ASR/syn_audio_man.mp3\'', 'parser.add_argument(\'--src_audio_path\', default=\'/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file/yc1_seq4.mp3\'')
#    f.seek(0)
#    f.write(content.encode('utf-8'))
#    f.truncate()

# 执行远程Python命令行
#command = f'python3 remote_script.py {remote_file_path} {other_arguments}'
#command = f'python3 /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/scripts/prepare_testing_files.py'
stdin, stdout, stderr = ssh.exec_command(command)
output = stdout.read().decode('utf-8')

# 获取训练结果到本地
#sftp.get(remote_result_path, local_result_path)

# 关闭sftp和SSH连接
#sftp.close()
ssh.close()

# 输出命令行执行结果
print(output)
