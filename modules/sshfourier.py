import paramiko

# 定义跳板机和目标机器的连接信息
gauss_hostname = '202.120.38.69'
gauss_port = 5566
gauss_username = 'gyh17'
gauss_password = 'Sp1ch!ab'
fourier_hostname='fourier'
fourier_password='Sp1ch!ab'
jump_host = {
    'hostname': '202.120.38.69',
    'username': 'gyh17',
    'password': 'Sp1ch!ab',
    'port': 5566,
}

target_host = {
    'hostname': 'fourier',
    'username': 'gyh17',
    'password': 'Sp1ch!ab',
    'port': 22,
}

# 建立跳板机连接
ssh_jump = paramiko.SSHClient()
ssh_jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_jump.connect(**jump_host)

# 使用跳板机连接建立目标机连接
proxy_cmd = f'ssh fourier'
ssh_target = ssh_jump.invoke_shell()
ssh_target.send(proxy_cmd + '\n')
ssh_target.send(fourier_password + '\n')
# 这里可以继续在目标机器上执行命令
stdin, stdout, stderr = ssh_target.exec_command('nvidia-smi')
print(stdout.read().decode('gb18030'))

# 关闭连接
ssh_target.close()
ssh_jump.close()