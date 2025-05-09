#!/usr/bin/env python3

import gzip
import os.path
import re
import shutil
import sys

# all of the files I tried were using this encoding (Latin 1)
PPD_ENCODING = 'iso-8859-1'

# Parses Mac driver from /Library/Printers/PPDs/Contents/Resources
class MacPPD:
    def __init__(self, file_name):
        self.file_name = file_name
        self.full_path = f'/Library/Printers/PPDs/Contents/Resources/{file_name}'
        self.is_installed = os.path.isfile(self.full_path)
        self.lines = []
        
        lines_with_eol = []
        if self.is_installed:
            if file_name.lower().endswith('.gz'):
                with gzip.open(self.full_path, 'rt', encoding=PPD_ENCODING) as f:
                    lines_with_eol = f.readlines()
            elif file_name.lower().endswith('.ppd'):
                with open(self.full_path, 'r', encoding=PPD_ENCODING) as f:
                    lines_with_eol = f.readlines()

        # readlines doesn't remove end-of-line characters so we remove them manually
        for line in lines_with_eol:
            self.lines.append(line.strip())

    def _get_value(self, attribute):
        for line in self.lines:
            if line.startswith(f'*{attribute}'):
                return line.split()[1:]
        return ''

# Mac-specific attributes
MAC_ATTRS = [
    'APDialogExtension',
    'APDuplexRequiresFlippedMargin',
    'APHelpBook',
    'APICADriver',
    'APPrinterIconPath',
    'APPrinterLowInkTool',
    'APPrinterPreset',
    'APPrinterUtilityPath',
    'APScannerOnly',
    'APScanAppBundleID'
]

def convert(mac_ppd, dest_dir):
    if not dest_dir.endswith('/'):
        dest_dir += '/'
    name_no_ext = mac_ppd.file_name.split('.')[0]
    
    out_ppd = []

    for line in mac_ppd.lines:
        ignore_line = False

        if line.startswith('*%Platform:'):
            line = '*%Platform: Linux'
        elif line.startswith('*PCFileName:'):
            line = f'*PCFileName: "{mac_ppd.file_name}"'

        # covers both cupsFilter and cupsFilter2
        if not ignore_line and '*cupsFilter' in line:
            print('Warning: filter will be ignored:', line)
            ignore_line = True

        # ICC color profiles will be copied (if present)
        if not ignore_line and '*cupsICCProfile' in line:
            icc = re.search(r'"(?:.*\s)?(/[^"]+)"', line)
            if icc:
                icc_path = icc.group(1)
                if os.path.isfile(icc_path):
                    icc_name = os.path.basename(icc_path)
                    icc_copy = f'{dest_dir}{name_no_ext}_{icc_name}'
                    shutil.copy(icc.group(1), f'{dest_dir}{name_no_ext}_{icc_name}')
                    line = line.replace(icc_path, icc_copy)
                    out_ppd.append(line)
                    print(f'Info: ICC profile copied to {icc_copy}, please update path in PPD file when coping to target destination')
                else:
                    print(f"Warning: ICC profile at {icc_path} doesn't exist, skipping")
            else:
                print('Warning: cannot extract ICC profile path:', line)
            ignore_line = True 

        # ignore know Mac-specific attributes
        if not ignore_line:
            for attr in MAC_ATTRS:
                if attr in line:
                    print('Info: macOS specific attribute, will be ignored: ' + line)
                    ignore_line = True
                    break

        # ignore attributes containing Mac-specific paths
        if not ignore_line and '/Library/Printers' in line:
            print('Info: macOS specific path: ' + line)
            ignore_line = True

        if not ignore_line:
            out_ppd.append(line)

    with open(dest_dir + mac_ppd.file_name, 'w', encoding=PPD_ENCODING) as f:
        for line in out_ppd:
            f.write(line + '\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], '<PPD file>', '<output directory>')
        print('  PPD file is file name in /Library/Printers/PPDs/Contents/Resources')
        sys.exit(1)
    
    ppd = MacPPD(sys.argv[1])
    if ppd.is_installed:
        convert(ppd, sys.argv[2])
    else:
        print('Error:', ppd.full_path, 'not found')

