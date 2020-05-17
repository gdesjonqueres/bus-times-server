import subprocess

subprocess.run(['cp', '/home/guigui/toto.txt',
                '/home/guigui/titi.txt'], check=True)
print('it worked')
