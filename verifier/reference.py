# Validates AT, FF, and DC tests against the WOFF2 reference implementation.
# UA tests should be checked in Chrome, which uses the reference.

import gflags
import os
import shutil
import subprocess
import tempfile

FLAGS = gflags.FLAGS

gflags.DEFINE_string('woff2_bin_dir', '~/oss/woff2',
                     'Where to find woff2_{de,}compress')

_IMPLEMENTATIONS = {
  'Reference': lambda f: Woff2Decompress(f)
}

def Woff2Decompress(path):
  woff2_dec = os.path.join(os.path.expanduser(FLAGS.woff2_bin_dir), 'woff2_decompress')
  return subprocess.call([woff2_dec, path]) == 0

def main():
  with open('Format/expectations.txt') as f:
    expectations = [[e.strip() for e in l.split(',')] for l in f]

  for l in expectations:
    l[2] = l[2].strip() == 'True'

  tmp_dir = tempfile.mkdtemp(prefix='woff2ctscheck')

  for impl_name, impl_fn in _IMPLEMENTATIONS.iteritems():
    test_results = {}

    print '==========================================='
    print 'Per-file results for %s' % impl_name
    print '==========================================='

    for identifier, links, expectation in expectations:
      woff2_original = os.path.join('Format/Tests/xhtml1/', identifier + '.woff2')
      woff2_temp = os.path.join(tmp_dir, os.path.basename(woff2_original))

      if not os.path.isfile(woff2_temp):
        shutil.copy(woff2_original, woff2_temp)

      actual = impl_fn(woff2_temp)
      msg = 'fail (expect %r != actual %r)' % (expectation, actual)
      if actual == expectation:
        msg = 'pass'
      print '%s %s %s %s' % (links, os.path.basename(woff2_original), impl_name, msg)

      for link in [l for l in links.split(' ') if l]:
        ref = '#' + link.split('#')[-1]
        if '/WOFF/' in link:
          ref = 'woff1:' + ref
        # avoid overwriting a fail result with a pass
        if actual == expectation and ref in test_results:
          continue
        test_results[ref] = actual == expectation

    print '==========================================='
    print 'Per-test results for %s' % impl_name
    print '==========================================='
    for ref in sorted(test_results):
      print '%s %r' % (ref, test_results[ref])

if __name__ == "__main__":
    main()
