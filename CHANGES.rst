Release 0.2.0 (released Feb 20, 2020)
-------------------------------------

* Fix api_path handling to be compatible with more recent hawkBit versions
  (failed with '500: Server Error' before)
* Update to aiohttp 3.3.2 to improve timeout handling  (by Livio Bieri)
* Significant speed improvements by reading maximum of available data instead
  of using fixed chunk sizes (by Livio Bieri)
* Prefer https [download] over http [download-http] (by Livio Bieri)
* minor cleanups and documentation fixes

Release 0.1.0 (released Nov 20, 2017)
-------------------------------------

This is the initial release of the RAUC hawkBit Client.
