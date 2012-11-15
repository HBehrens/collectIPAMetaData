#!/usr/bin/env python
from pprint import pprint
import json
import sys
import optparse

def key_for_bundle(bundle, primary="item_id"):
    return ("%s#%s" % (bundle[primary], bundle.get("version",""))).upper()


def print_stats(bundles):
    all_schemes = []
    all_app_ids = []
    all_bundles = set()
    for bundle in bundles:
        all_app_ids.append(bundle["item_id"])
        all_schemes.extend(bundle["url_schemes"])
        all_bundles.add(key_for_bundle(bundle))

    all_app_ids = set(all_app_ids)
    all_schemes = set(all_schemes)

    print "schemes: %d, apps: %d, bundles: %d" % (len(all_schemes), len(all_app_ids), len(all_bundles))

def loadMappings(filename):
    print "loading %s" % filename
    bundles = json.load(open(filename, 'r'))
    print_stats(bundles)
    return bundles

def mergeMappings(bundles_list):
    print "merging %d bundle lists" % len(bundles_list)

    items = {}
    for bundles in bundles_list:
        for bundle in bundles:
            bundle_key = key_for_bundle(bundle)

            if items.has_key(bundle_key):
                existing = items.get(bundle_key)
                def sanityCheck(key):
                    if existing.get(key, None) != bundle.get(key, None):
                        print "inconsistency: %s has different value for key %s" % (bundle_key, key)

                for key in ["bundle_id", "name", "url_schemes"]:
                    sanityCheck("")
            else:
                items[bundle_key] = bundle

    merged = items.values()
    merged.sort(key=lambda bundle:key_for_bundle(bundle, "bundle_id"))

    print_stats(merged)
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

def main():
    args = get_options()

    bundles_list = [loadMappings(f) for f in args[1]]
    merged = mergeMappings(bundles_list)

    fo = args[0].output_file
    if isinstance(fo, str):
        fo = open(fo, 'w')

    json.dump(merged, fo, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
