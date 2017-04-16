from random import Random


accessKeyId = ''
accessKeySecret = ''
host = ''

random = Random()
config_map = getConfigInfo('oss_server.config')

def random_string(randomlength):
    chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    length = len(chars) - 1
    random_str = ''
    for i in xrange(randomlength):
        random_str+=chars[random.randint(0, length)]
    
    return random_str


def getConfigInfo(file_name):
    key_value = {}
    with open(file_name,"r") as f:
        for line in f:
            line = line.strip('\n')
            array = line.split('=')
            key_value[array[0]] = array[1]
    print key_value
    accessKeyId = key_value['accessKeyId']
    accessKeySecret = key_value['accessKeySecret']
    host = key_value['host']

config_map = getConfigInfo('oss_server.config')

if __name__ == "__main__":
	print random_string(5)
	print config_map