import os
import traceback
from importlib import import_module

import yaml
import yaml.representer

from dmoj import judgeenv
from dmoj.utils.ansi import ansi_style

TEST_ON_TRAVIS = ['PY2', 'TEXT']


def main():
    result = {}

    judgeenv.env['runtime'] = {}
    judgeenv.env['extra_fs'] = {
        'PY2': [r'/home/travis/virtualenv/python2\.7'],
    }

    failed = False

    for name in TEST_ON_TRAVIS:
        executor = import_module('dmoj.executors.' + name)

        print ansi_style('%-34s%s' % ('Testing #ansi[%s](|underline):' % name, '')),

        if not hasattr(executor, 'Executor'):
            failed = True
            print ansi_style('#ansi[Does not export](red|bold) #ansi[Executor](red|underline)')
            continue

        if not hasattr(executor.Executor, 'autoconfig'):
            print ansi_style('#ansi[Could not autoconfig](magenta|bold)')
            continue

        try:
            data = executor.Executor.autoconfig()
            config = data[0]
            success = data[1]
            feedback = data[2]
            errors = '' if len(data) < 4 else data[3]
        except Exception:
            failed = True
            print ansi_style('#ansi[Autoconfig broken](red|bold)')
            traceback.print_exc()
        else:
            print ansi_style(['#ansi[%s](red|bold)', '#ansi[%s](green|bold)'][success] %
                             (feedback or ['Failed', 'Success'][success]))

            if success:
                result.update(config)
            else:
                if config:
                    print '  Attempted:'
                    print '   ', yaml.dump(config, default_flow_style=False).rstrip().replace('\n', '\n' + ' ' * 4)

                if errors:
                    print '  Errors:'
                    print '   ', errors.replace('\n', '\n' + ' ' * 4)
                failed = True

    print
    print ansi_style('#ansi[Configuration result](green|bold|underline):')
    print yaml.dump({'runtime': result}, default_flow_style=False).rstrip()
    raise SystemExit(int(failed))


if __name__ == '__main__':
    main()
