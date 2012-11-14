#!/usr/bin/env python
from pprint import pprint
import json
import sys
import optparse

def loadMappings(filename):
    mappings = json.load(open(filename, 'r'))
    if isinstance(mappings, dict):
        return mappings
    else:
        result = {}
        for mapping in mappings:
            for scheme in mapping['url_schemes']:
                ids = result.get(scheme, [])
                ids.append(mapping['item_id'])
                result[scheme] = ids
        return result

def mergeMappings(mappings_list):
    merged = {}
    for mappings in mappings_list:
        for scheme, ids in mappings.items():
            merged_ids = merged.get(scheme, [])
            merged_ids.extend(ids)
            merged_ids = list(set(merged_ids))
            merged_ids.sort()
            merged[scheme] = merged_ids
    return merged

def get_options():
    optp = optparse.OptionParser('usage: %prog [options] file1 file2 .. fileN"')

    optp.add_option('-o', '--outputfile', action='store', dest='output_file', default=sys.stdout,
        help='location to write the JSON to (default: stdout)')

    args = optp.parse_args()
    if len(args[1]) <= 0:
        optp.print_help()
        sys.exit(1)

    return args

def print_stats(mappings):
    all_schemes = []
    all_app_ids = []
    for scheme, app_ids in mappings.items():
        all_schemes.append(scheme)
        all_app_ids.extend(app_ids)
    all_app_ids = set(all_app_ids)

    print "schemes: %d, apps: %d" % (len(all_schemes), len(all_app_ids))

def main():
    args = get_options()

    mappings_list = [loadMappings(f) for f in args[1]]
    merged = mergeMappings(mappings_list)

    print_stats(merged)

    # sorted keys and line breaks at start, end and per scheme
    s= json.dumps(merged, sort_keys=True).replace('],', '],\n').replace('{', '{\n').replace('}','\n}')

    fo = args[0].output_file
    if isinstance(fo, str):
        fo = open(fo, 'w')
    fo.writelines(s)

if __name__ == '__main__':
    main()
