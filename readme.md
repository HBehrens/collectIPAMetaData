# Extract Meaningful Meta Data from IPAs

A set of scripts to extract and merge meta data from iOS apps such as _url schemes_, _app store id_, _supported iOS version_ etc. by scanning IPA files stored in your iTunes library on OS X.

## Extracting Data

To extract and store all your apps meta data into a JSON file call

```
./collectIPAMetaData.py -o myMetaData.json
```

The script tries to find IPAs in a set of default locations but can be asked to search your IPAs at specifiec directories or scan explicitly provided IPAs. Use the `--help` argument to learn about the possible options.

## Merging Data

If you want to merge your data with the one of this repository to __create a pull request__, use this command:

```
./mergeIPAMetaData.py -o ipaMetaData.json ipaMetaData.json myMetaData.json
```

Have a look at the statistics to see how much you added to the `ipaMetaData.json` in place, e.g.

```
loading ipaMetaData.json
schemes: 576, apps: 312, bundles: 754
loading myMetaData.json
schemes: 244, apps: 104, bundles: 104
merging 2 bundle lists
schemes: 598, apps: 329, bundles: 774
```
In this case you added 20 new bundles to the collection but only 17 apps. This can happen since each version of an app will be preserved. 22 url schemes had been added due to the merge, meaning that even more [apps will be connected via url schemes][openHandleUrl] :)

## Derive Data for iHasApp

To add new mappings in the `schemeApps.json` format of [iHasApp][iHasApp] use this command:

```
./mergeIHasAppMappings.py -o schemeApps.json ignored/schemeApps.json ipaMetaData.json
```


## Contributions

This extractor and merger has been written by [Heiko Behrens](http://HeikoBehrens.net) ([twitter](http://twitter.com/hbehrens)) to derive meta data for the [OpenHandleURL.com][openHandleUrl], [BeamApp][BeamApp] and [iHasApp][iHasApp]. Parts of the plist logic is based on [https://github.com/apperian/iOS-checkIPA](https://github.com/apperian/iOS-checkIPA).

[openHandleUrl]: http://handleOpenUrl.com
[iHasApp]: https://github.com/danielamitay/iHasApp
[createPullRequest]: http://createPullRequest
[BeamApp]: http://getBeamApp.com

