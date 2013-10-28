################################################################################
# License
################################################################################
# Copyright (c) 2007 Jeremy Whitlock.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import os, shutil, sys, unittest, coverage_color

sys.path = [os.path.join(os.path.dirname(__file__), "lib")] + sys.path

import coverage
from django.test.simple import run_tests as django_test_runner

from django.conf import settings

coverage = coverage.coverage()

def test_runner_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
  """Custom test runner.  Follows the django.test.simple.run_tests() interface."""
  print "cs test_runner_with_coverage " + str(getattr(settings, 'COVERAGE_MODULES')) + " , " + str(test_labels)
  
  coverage.use_cache(0) # Do not cache any of the coverage.py stuff
  coverage.start()
  
  # Start code coverage before anything else if necessary
#   if hasattr(settings, 'COVERAGE_MODULES') and not test_labels:
#     print "cs coverage start"
#     coverage.use_cache(0) # Do not cache any of the coverage.py stuff
#     coverage.start()

  test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)


  coverage.stop()

  if not os.path.exists(settings.COVERAGE_DIR):
    os.makedirs(settings.COVERAGE_DIR)

  coverage.html_report(directory='coverage')

  coverage.erase();

  # Stop code coverage after tests have completed
#   if hasattr(settings, 'COVERAGE_MODULES') and not test_labels:
#     coverage.stop()
# 
#     # Print code metrics header
#     print ''
#     print '----------------------------------------------------------------------'
#     print ' Unit Test Code Coverage Results'
#     print '----------------------------------------------------------------------'

#   coverage_modules = []
#   for module in settings.COVERAGE_MODULES:
#     coverage_modules.append(__import__(module, globals(), locals(), ['']))
#     
#   print "cs coverage_modules: " + str(coverage_modules)
    
#   for module_string in settings.COVERAGE_MODULES:
#     module = __import__(module_string, globals(), locals(), [""])
#     f,s,m,mf = coverage.analysis(module)    
#     fp = file(os.path.join(settings.COVERAGE_DIR, module_string + ".html"), "wb")
#     coverage_color.colorize_file(f, outstream=fp, not_covered=mf)
#     fp.close()
#   coverage.report(coverage_modules, show_missing=1)

#   coverage.erase();

  # Report code coverage metrics
#   if hasattr(settings, 'COVERAGE_MODULES') and not test_labels:
#     coverage_modules = []
#     for module in settings.COVERAGE_MODULES:
#       coverage_modules.append(__import__(module, globals(), locals(), ['']))
# 
#     coverage.report(coverage_modules, show_missing=1)
    
    # Print code metrics footer
#     print '----------------------------------------------------------------------'

  return test_results

# test_runner_with_coverage()
