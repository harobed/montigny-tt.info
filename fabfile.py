# -*- coding: utf8 -*-
import os

from fabric.api import task, run, env, cd, settings
from fabtools.vagrant import ssh_config, _settings_dict
import fabtools  # NOQA
from fabtools import require

import mechanize

here = os.path.abspath(os.path.dirname(__file__))


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'

    env['mysql_user'] = 'root'
    env['mysql_password'] = os.environ.get('MYSQL_PASSWORD', 'password')


VIRTUALHOST_TPL = """
{{default aliases=[] }}
{{default allow_override=None }}
<VirtualHost *:80>
    ServerName {{hostname}}
    {{for a in aliases}}
    ServerAlias {{a}}
    {{endfor}}

    DocumentRoot {{document_root}}

    <Directory {{document_root}}>
        Options Indexes FollowSymLinks MultiViews

        {{if allow_override}}
        AllowOverride {{allow_override}}
        {{else}}
        AllowOverride All
        {{endif}}

        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
"""


@task
def wordpress_config():
    env['wordpress'] = {
        'unix_user': 'wp-montigny-tt',
        'url': 'beta.montigny-tt.info',
        'url_aliases': [],
        'database_name': 'wpmontignytt',
        'database_user': 'wpmontignytt',
        'database_password': 'password'
    }


def _add_user(*args, **kwargs):
    require.user(*args, **kwargs)
    if 'name' not in kwargs:
        user = args[0]
    else:
        user = kwargs['name']

    if not fabtools.files.is_file('/home/%s/.ssh/authorized_keys' % user):
        run('mkdir -p /home/%s/.ssh/' % user)
        run('cp /root/.ssh/authorized_keys /home/%s/.ssh/' % user)
        run('chown %(user)s:%(user)s /home/%(user)s/.ssh/ -R' % {'user': user})


@task
def install():
    fabtools.require.system.locale('fr_FR.UTF-8')

    fabtools.deb.update_index()
    fabtools.deb.preseed_package('mysql-server', {
        'mysql-server/root_password': ('password', env['mysql_password']),
        'mysql-server/root_password_again': ('password', env['mysql_password'])
    })
    require.deb.packages([
        'build-essential',
        'devscripts',
        'locales',
        'apache2',
        'mysql-server',
        'mysql-client',
        'php5',
        'php5-mysql',
        'libapache2-mod-php5',
        'vim',
        'mc',
        'curl',
        'libmysqlclient-dev'
    ])

    _add_user(
        name=env['wordpress']['unix_user'],
        password=None,
        shell='/bin/bash'
    )
    require.mysql.user(env['wordpress']['database_user'], env['wordpress']['database_password'])
    require.mysql.database(env['wordpress']['database_name'], owner=env['wordpress']['database_user'])
    require.directory('/home/%s/prod/' % env['wordpress']['unix_user'])
    run(
        'chown %(unix_user)s:%(unix_user)s /home/%(unix_user)s/prod/'
        % {
            'unix_user': env['wordpress']['unix_user']
        }
    )
    with settings(user=env['wordpress']['unix_user']):
        with cd('/home/%s/prod/' % env['wordpress']['unix_user']):
            require.file(url='http://fr.wordpress.org/latest-fr_FR.zip')
            run('unzip latest-fr_FR.zip')
            run('mv wordpress www')
            run('rm latest-fr_FR.zip')

    with cd('/home/%s/prod/' % env['wordpress']['unix_user']):
        run('chown %s:www-data www/ -R' % env['wordpress']['unix_user'])
        run('chmod ug+rwX www/ -R')

    run('rm -f /etc/apache2/sites-enabled/000-default')
    require.apache.site(
        env['wordpress']['url'],
        template_contents=VIRTUALHOST_TPL,
        hostname=env['wordpress']['url'],
        document_root='/home/%s/prod/www/' % env['wordpress']['unix_user'],
        aliases=env['wordpress']['url_aliases'],
        enable=True
    )
    fabtools.apache.restart()

    br = mechanize.Browser()
    br.open('http://%s/wp-admin/setup-config.php?step=1' % env['wordpress']['url'])
    br.select_form(predicate=lambda form: form.attrs.get('action') == 'setup-config.php?step=2')
    br['dbname'] = env['wordpress']['database_name']
    br['uname'] = env['wordpress']['database_user']
    br['pwd'] = env['wordpress']['database_password']
    br.submit()

    br.open('http://%s/wp-admin/install.php' % env['wordpress']['url'])
    br.select_form(predicate=lambda form: form.attrs.get('id') == 'setup')
    br['weblog_title'] = 'Montigny les Metz - Tennis de Table'
    br['user_name'] = 'admin'
    br['admin_password'] = 'password'
    br['admin_password2'] = 'password'
    br['admin_email'] = 'contact@stephane-klein.info'
    br.submit()


@task
def uninstall():
    fabtools.mysql.drop_database(env['wordpress']['database_name'])
    fabtools.mysql.drop_user(env['wordpress']['database_user'])
    run('rm -rf /home/%s/prod/' % env['wordpress']['unix_user'])
    fabtools.apache.disable_site(env['wordpress']['url'])
    fabtools.apache.restart()
