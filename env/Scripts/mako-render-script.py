#!C:\env\HomeBanking\env\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'Mako','console_scripts','mako-render'
__requires__ = 'Mako'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('Mako', 'console_scripts', 'mako-render')()
    )
