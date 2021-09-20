import subprocess
import sys
import re

def bash(cmd):

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
    tmp = proc.stdout.read()
    r = tmp.decode('cp1251')
    return r

if __name__ == '__main__':

    lines = bash('nvidia-smi').split('\n')

    pids = False
    procs = []

    for line in lines:
        if line.startswith('| Processes'):
            pids = True
            continue

        if pids:
            if len(line.split()) >= 6:
                _, gpu, pid, _, cmd, gram = line.split()[0:6]
                if pid != 'PID':
                    procs.append([gpu, pid, cmd, gram])

    lines = bash("docker ps -qa | xargs docker inspect --format '{{.State.Pid}}, {{.Name}}, {{.Config.User}}, {{.Config.Image}}'").split('\n')
    dockers = {}
    for line in lines:
        if len(line.split(',')) == 4:
            pid, name, user, image = line.split(',')
            dockers[pid] = (name, user, image)

    #print(dockers)

    lines = bash("ps -A -o 'pid,user,pcpu,etime,cmd' --no-header").split('\n')
    ps_all = {}

    for line in lines:
        cols = line.strip().split(' ')
        cols = filter(lambda x : x, cols)
        if len(cols)>=3:
            ps_pid = cols[0]
            user = cols[1]
            pcpu = cols[2]
            etime = cols[3]
            ps_cmd = ' '.join(cols[4:])

            ps_all[ps_pid] = (user, ps_cmd, pcpu, etime)

    format_str = '%5s %5s %5s %10s %25s %25s %10s %15s %-30s'

    print(format_str % ('GPU', 'PID', 'CPU', 'GPU RAM',\
                     'DOCKER_NAME', 'DOCKER IMAGE', 'USER', 'TIME', 'HOMEDIR'))

    print('-' * 150)
    for gpu, pid, cmd, gram in procs:

        data = {}

        res = bash('pstree -sg %s' % pid)

        pids = set(re.findall(r'.([0-9]+[0-9]*)', res))
        #print('GPU =', gpu, ', PID =', pid, ', CMD =', cmd, ', GRAM =', gram)
        data['gpu'] = gpu
        data['pid'] = pid
        data['gpu_cmd'] = cmd
        data['gpu_ram'] = gram
        #print('process info: ', bash("ps -o 'pid,user,cmd' --no-header -p %s" % pid))

        data['homedir'] = bash('pwdx %s' % pid).split(':')[1].strip()

        #lines = bash("ps -o 'pid,user,cmd' --no-header -p %s" % pid).strip().split(' ')
        #ps_pid = lines[0]
        #user = lines[1]
        #ps_cmd = ' '.join(lines[2:])
        #print('User', user, 'pid', ps_pid, 'cmd', ps_cmd)
        if pid not in ps_all:
            ps_all[pid] = ['?', '?', '?']
        data['ps_user'] = ps_all[pid][0]
        data['ps_pid'] = pid
        data['ps_cmd'] = ps_all[pid][1]
        data['ps_pcpu'] = ps_all[pid][2]
        data['ps_etime'] = ps_all[pid][3]
        #print('process info: ', bash("ps -p %s u" % pid).split('\\n')[1])
        data['parent_pids'] = pids
        for pid in pids:
            if pid in dockers:
                #print('docker: pid =', pid, dockers[pid])
                data['docker_pid'] = dockers[pid]
                data['docker_name'] = dockers[pid][0]
                data['docker_user'] = dockers[pid][1]
                data['docker_image'] = dockers[pid][2]

        #data['ps_cmd'] = data['homedir']

        print(format_str % (data['gpu'], data['pid'], data['ps_pcpu'], data['gpu_ram'],\
                     data.get('docker_name', '-'), data.get('docker_image', '-'), data['ps_user'], data['ps_etime'], data['homedir'][0:70]))

        #print(format_str % tuple([''] * 6 + [data['homedir']]))
