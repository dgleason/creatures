from fabric.api import local

def prepare_deployment(branch_name):
    local('python manage.py test baseapp')
    local('git add -p && git commit')
    local('git checkout master && git merge ' + branch_name)

from fabric.api import lcd

def deploy():
    with lcd('/home/project/myproject/myproject/'):
        local('git pull /dev/creatures/myproject/myproject/)
        local('python manage.py migrate baseapp')
        local('python manage.py test baseapp')
        run('touch ~/%s/tmp/restart.txt' % env.host)
