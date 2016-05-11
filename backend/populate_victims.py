from django import setup
import os
import yaml
from django.core.exceptions import ObjectDoesNotExist
from backend.settings import BASE_DIR
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
setup()

from breach.models import Target, Victim


def select_victim(victims):
    print '[*] Victims:'
    for i, v in enumerate(victims):
        print '\tID: {}  -  Victim: {} ({})'.format(i, v[0], v[1]['sourceip'])

    try:
        vic_ids = str(input('[*] Choose victim ids separated by commas, or leave empty to select all: '))
    except SyntaxError:
        return [vic[1] for vic in victims]

    vic_ids = [i.strip() for i in vic_ids.split(',')]
    if '' in vic_ids:
        vic_ids.remove('')

    try:
        victim_list = []
        for vid in vic_ids:
            victim_list.append(victims[int(vid)][1])
    except KeyError:
        print '[!] Invalid victim id.'
        exit(1)
    return victim_list


def select_target():
    print '[*] Targets:'
    for t in Target.objects.all():
        print '\tID: {}  -  Target: {}'.format(t.id, t.host)
    try:
        tids = str(input('[*] Choose target ids separated by commas, or leave empty to select all: '))
    except SyntaxError:
        return Target.objects.all()

    tids = [i.strip() for i in tids.split(',')]
    if '' in tids:
        tids.remove('')

    try:
        target_list = []
        for t in tids:
            target_list.append(Target.objects.get(id=int(t)))
    except ObjectDoesNotExist:
        print '[!] Invalid target id.'
        exit(1)
    return target_list


def create_victim(target, victim):
    for m in Victim.METHOD_CHOICES:
        if victim['method'] == m[1]:
            victim['method'] = m[0]
            break

    v = Victim(
        target=target,
        snifferendpoint=victim['snifferendpoint'],
        sourceip=victim['sourceip'],
        method=victim['method'],
        realtimeurl=victim['realtimeurl']
    )
    v.save()

    print '''Created Victim:
             \tvictim_id: {}
             \ttarget: {}
             \tsnifferendpoint: {}
             \tsourceip: {}
             \tmethod: {}
             \trealtimeurl: {}'''.format(
                v.id,
                v.target.host,
                v.snifferendpoint,
                v.sourceip,
                v.method,
                v.realtimeurl
            )


if __name__ == '__main__':
    try:
        with open(os.path.join(BASE_DIR, 'victim_config.yml'), 'r') as ymlconf:
            cfg = yaml.load(ymlconf)
    except IOError, err:
        print 'IOError: %s' % err
        exit(1)
    victims = list(cfg.items())

    try:
        victim_list = select_victim(victims)
        target_list = select_target()
        for victim in victim_list:
            for target in target_list:
                create_victim(target, victim)
    except KeyboardInterrupt:
        print ''
        exit(1)
