#!/usr/bin/env python

from pprint import pprint
import sys
import os
import tempfile
import shutil
import re
import zipfile
import plistlib
import optparse
import json

class ParseIPA(object):
    # ParseIPA is based on https://github.com/apperian/iOS-checkIPA
    plist_file_rx = re.compile(r'Payload/.+?\.app/Info.plist$')
    metadata_file_rx = re.compile(r'^iTunesMetadata.plist$')
    xml_rx = re.compile(r'<\??xml')

    def __init__(self, ipa_filename):
        self.info_plist_data = {}
        self.provision_data = {}
        self.errors = []
        self.ipa_filename = ipa_filename
        self.full_path_plist_filename = ''
        self.temp_directory = ''
        self.verbose = False

    def get_filename_from_ipa(self, filetype):
        zip_obj = zipfile.ZipFile(self.ipa_filename, 'r')

        if filetype == 'Info':
            regx = ParseIPA.plist_file_rx
        elif filetype == "iTunesMetadata":
            regx = ParseIPA.metadata_file_rx
        else:
            raise "unknown typetype" % filetype

        filenames = zip_obj.namelist()
        filename = ''
        for fname in filenames:
            if regx.search(fname):
                filename = fname
                break
        return {'filename': filename, 'zip_obj': zip_obj}
        # end get_filename_from_ipa()

    def extract_plist_data(self, name):
        extract_info = self.get_filename_from_ipa(name)
        zip_obj = extract_info['zip_obj']
        plist_filename = extract_info['filename']

        data = {}
        if plist_filename == '':
            self.errors.append('%s.plist file not found in IPA' % name)
        else:
            content = zip_obj.read(plist_filename)
            if ParseIPA.xml_rx.match(content):
                data = plistlib.readPlistFromString(content)
            else:
                self.temp_directory = tempfile.mkdtemp()

                zip_obj.extract(plist_filename, self.temp_directory)
                fullpath_plist = '%s/%s' % (self.temp_directory, plist_filename)

                os_info = os.uname()
                if os_info[0] == 'Linux':
                    cmd = 'plutil -i "%s" -o "%s"' % (fullpath_plist, fullpath_plist)
                else:
                    cmd = 'plutil -convert xml1 "%s"' % fullpath_plist

                if self.verbose:
                    pprint(cmd)

                os.system(cmd)
                data = plistlib.readPlist(fullpath_plist)
                # end if plist == ''
        return data

    def extract_info_plist_data(self):
        self.info_plist_data = self.extract_plist_data('Info')

    def extract_itunes_meta_data(self):
        self.itunes_meta_data = self.extract_plist_data("iTunesMetadata")

    def is_valid_zip_archive(self):
        return zipfile.is_zipfile(self.ipa_filename)

def process_ipa(ipa_filename, verbose = False):
    print 'processing %s' % ipa_filename

    errors = []
    parse = ParseIPA(ipa_filename)
    parse.verbose = verbose

    if not parse.is_valid_zip_archive():
        errors.append('not a valid zip archive [%s]' % ipa_filename)
    else:
        parse.extract_info_plist_data()
        parse.extract_itunes_meta_data()
        errors.extend(parse.errors)

    if len(errors) == 0:
        if verbose:
            print('Info.plist')
            pprint(parse.info_plist_data)
            print('iTunesMetadata.plist')
            pprint(parse.itunes_meta_data)

        url_schemes = []
        for url_type in parse.info_plist_data.get('CFBundleURLTypes', []):
            for url_scheme in url_type.get('CFBundleURLSchemes', []):
                url_schemes.append(url_scheme)

        result = {
            'name': parse.itunes_meta_data['itemName'],
            'item_id': parse.itunes_meta_data['itemId'],
            'bundle_id': parse.itunes_meta_data['softwareVersionBundleId'],
            'url_schemes': url_schemes
        }

        if parse.itunes_meta_data.has_key('bundleVersion'):
            result['version'] = parse.itunes_meta_data['bundleVersion']
        if parse.itunes_meta_data.has_key('bundleShortVersionString'):
            result['short_version'] = parse.itunes_meta_data['bundleShortVersionString']

        if verbose:
            pprint(result)


        # clean up tmp directory tree
        try:
            if parse.temp_directory != '':
                shutil.rmtree(parse.temp_directory)
        except IOError, ex:
            print(str(ex))

        return result

    else:
        pprint(errors)
        return None

def process_ipas_in_list(file_list, fp, verbose):
    results = []
    for file_name in file_list:
        result = process_ipa(file_name, verbose)
        if result and len(result["url_schemes"]) > 0:
            result["url_schemes"].sort()
            results.append( result )

    results.sort(key=lambda bundle:("%s#%s" % (bundle["bundle_id"], bundle.get("version",""))).upper())

    json.dump(results, fp, indent=2, sort_keys=True)

def process_ipas_in_dir(dir, fp, verbose):
    dir = os.path.expanduser(dir)
    if not os.path.isdir(dir):
        print "%s is not a valid directory" % dir
        sys.exit(2)

    process_ipas_in_list([os.path.join(dir, f) for f in os.listdir(dir) if re.match(r'.*\.ipa$', f)], fp, verbose)

def get_options():
    optp = optparse.OptionParser(epilog='When omitting -i or -d arguments, all IPAs stored in iTunes will be scanned.')

    optp.add_option('-i', '--ipafile', action='store', dest='input_file',
        help='scan single IPA')
    optp.add_option('-o', '--outputfile', action='store', dest='output_file', default=sys.stdout,
        help='location to write the JSON to (default: stdout)')
    default_dir = '~/Music/iTunes/Mobile Applications'
    optp.add_option('-d', '--directory', action='store', dest='directory',
        default=default_dir,
        help='scan all IPAs in directory (default: %s)' % default_dir)


    optp.add_option('-v', '--verbose', action='store_true',
        dest='verbose', default=False,
        help='print data structures to stdout')

    opts_args = optp.parse_args()
    return opts_args[0]

def main():
    options = get_options()

    # Mac OS already should have the plutil command utility installed.
    # The following message is primarily for (Debian-based) Linux systems.
    plutil_check = os.system('which plutil >/dev/null')
    if plutil_check != 0:
        print '''The program 'plutil' is currently not installed. You can install it by typing:
                sudo apt-get install libplist-utils'''
        sys.exit(1)

    if isinstance(options.output_file, str):
        options.output_file = open(options.output_file, 'w')

    if options.input_file:
        process_ipas_in_list([options.input_file], options.output_file, options.verbose)
    else:
        process_ipas_in_dir(options.directory, options.output_file, options.verbose)

if __name__ == '__main__':
    main()
