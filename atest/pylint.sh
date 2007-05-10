# $Progeny$
#
#   Copyright 2005 Progeny Linux Systems, Inc.
#
#   This file is part of PDK.
#
#   PDK is free software; you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   PDK is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
#   License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PDK; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

# run pylint on the pdk module
#
# NOTE: Currently a lot is turned off. I suggest starting with turning on
# variable checking first, then miscellaneous, and later, basic.
# See: enable-variable, enable-... below.

PYLINT_OPTS="--disable-msg=W0142 --disable-msg=R0201"

cat >pylintrc <<EOF
# lint Python modules using external checkers.
#
#     This is the main checker controling the other ones and the reports
#     generation. It is itself both a raw checker and an astng checker in order
#     to:
#     * handle message activation / deactivation at the module level
#     * handle some basic but necessary stats'data (number of classes, methods...)
#
# This checker also defines the following reports:
#   * R0001: Total errors / warnings
#   * R0002: % errors / warnings by module
#   * R0003: Messages
#   * R0004: Global evaluation
#
[MASTER]
# Add <file or directory> to the black list. It should be a base name, not a
# path. You may set this option multiple times.
ignore=CVS

# Pickle collected data for later comparisons.
persistent=yes

# Set the cache size for astng objects.
cache-size=500



[REPORTS]
# Tells wether to display a full report or only the messages
reports=no

# Use HTML as output format instead of text
html=no

# Use a parseable text output format, so your favorite text editor will be able
# to jump to the line corresponding to a message.
parseable=no

# Colorizes text output using ansi escape codes
color=no

# Put messages in a separate file for each module / package specified on the
# command line instead of printing them on stdout. Reports (if any) will be
# written in a file name "pylint_global.[txt|html]".
files-output=no

# Python expression which should return a note less than 10 (10 is the highest
# note).You have access to the variables errors warning, statement which
# respectivly contain the number of errors / warnings messages and the total
# number of statements analyzed. This is used by the global evaluation report
# (R0004).
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)

# Add a comment according to your evaluation note. This is used by the global
# evaluation report (R0004).
comment=no

# Include message's id in output
include-ids=yes



# checks for
#     * unused variables / imports
#     * undefined variables
#     * redefinition of variable from builtins or from an outer scope
#     * use of variable before assigment
#
[VARIABLES]
# Enable / disable this checker
enable-variables=yes

# Tells wether we should check for unused import in __init__ files.
init-import=no

# List of variable names used for dummy variables (i.e. not used).
dummy-variables=_,dummy,i



# checks for :
#     * doc strings
#     * modules / classes / functions / methods / arguments / variables name
#     * number of arguments, local variables, branchs, returns and statements in
# functions, methods
#     * required module attributes
#     * dangerous default values as arguments
#     * redefinition of function / method / class
#     * uses of the global statement
#
# This checker also defines the following reports:
#   * R0101: Statistics by type
#
[BASIC]
# Enable / disable this checker
enable-basic=yes

# Required attributes for module, separated by a comma
#required-attributes=__revision__
required-attributes=

# Regular expression which should only match functions or classes name which do
# not require a docstring
no-docstring-rgx=__.*__

# Regular expression which should only match correct module names
module-rgx=(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$

# Regular expression which should only match correct module level names
const-rgx=[A-Za-z_][A-Za-z0-9_]{1,40}$

# Regular expression which should only match correct class names
class-rgx=[a-zA-Z_][a-zA-Z0-9_]+$

# Regular expression which should only match correct function names
function-rgx=[a-z_][A-Za-z0-9_]{1,40}$

# Regular expression which should only match correct method names
method-rgx=[a-z_][A-Za-z0-9_]{1,40}$

# Regular expression which should only match correct instance attribute names
attr-rgx=[a-z_][A-Za-z0-9_]{1,40}$

# Regular expression which should only match correct argument names
argument-rgx=[a-z_][A-Za-z0-9_]{,40}$

# Regular expression which should only match correct variable names
variable-rgx=[a-z_][A-Za-z0-9_]{,40}$

# Regular expression which should only match correct list comprehension /
# generator expression variable names
inlinevar-rgx=[A-Za-z_][A-Za-z0-9_]*$

# Good variable names which should always be accepted, separated by a comma
good-names=i,j,k,ex,Run,_

# Bad variable names which should always be refused, separated by a comma
bad-names=foo,bar,baz,toto,tutu,tata

# List of builtins function names that should not be used, separated by a comma
bad-functions=map,filter,apply,input



# checks for sign of poor/misdesign:
#     * number of methods, attributes, local variables...
#     * size, complexity of functions, methods
#
[DESIGN]
# Enable / disable this checker
enable-design=no

# Maximum number of arguments for function / method
max-args=5

# Maximum number of locals for function / method body
max-locals=15

# Maximum number of return / yield for function / method body
max-returns=6

# Maximum number of branch for function / method body
max-branchs=12

# Maximum number of statements in function / method body
max-statements=50

# Maximum number of parents for a class (see R0901).
max-parents=7

# Maximum number of attributes for a class (see R0902).
max-attributes=7

# Minimum number of public methods for a class (see R0903).
min-public-methods=2

# Maximum number of public methods for a class (see R0904).
max-public-methods=20



# checks for
#     * external modules dependencies
#     * relative / wildcard imports
#     * cyclic imports
#     * uses of deprecated modules
#
# This checker also defines the following reports:
#   * R0401: External dependencies
#   * R0402: Modules dependencies graph
#
[IMPORTS]
# Enable / disable this checker
enable-imports=yes

# Deprecated modules which should not be used, separated by a comma
deprecated-modules=regsub,string,TERMIOS,Bastion,rexec

# Create a graph of every (i.e. internal and external) dependencies in the given
# file (report R0402 must not be disabled)
import-graph=

# Create a graph of external dependencies in the given file (report R0402 must
# not be disabled)
ext-import-graph=

# Create a graph of internal dependencies in the given file (report R0402 must
# not be disabled)
int-import-graph=



# checks for :
#     * methods without self as first argument
#     * overriden methods signature
#     * access only to existant members via self
#     * attributes not defined in the __init__ method
#     * supported interfaces implementation
#     * unreachable code
#
[CLASSES]
# Enable / disable this checker
enable-classes=yes

# List of interface methods to ignore, separated by a comma. This is used for
# instance to not check methods defines in Zope's Interface base class.
ignore-iface-methods=isImplementedBy,deferred,extends,names,namesAndDescriptions,queryDescriptionFor,getBases,getDescriptionFor,getDoc,getName,getTaggedValue,getTaggedValueTags,isEqualOrExtendedBy,setTaggedValue,isImplementedByInstancesOf,adaptWith,is_implemented_by

# Tells wether missing members accessed in mixin class should be ignored. A
# mixin class is detected if its name ends with "mixin" (case insensitive).
ignore-mixin-members=yes



# checks for
#     * excepts without exception filter
#     * string exceptions
#
[EXCEPTIONS]
# Enable / disable this checker
enable-exceptions=yes



# does not check anything but gives some raw metrics :
#     * total number of lines
#     * total number of code lines
#     * total number of docstring lines
#     * total number of comments lines
#     * total number of empty lines
#
# This checker also defines the following reports:
#   * R0701: Raw metrics
#
[METRICS]
# Enable / disable this checker
enable-metrics=yes



# checks for similarities and duplicated code. This computation may be
#     memory / CPU intensive, so you should disable it if you experiments some
#     problems.
#
# This checker also defines the following reports:
#   * R0801: Duplication
#
[SIMILARITIES]
# Enable / disable this checker
enable-similarities=yes

# Minimum lines number of a similarity.
min-similarity-lines=4

# Ignore comments when computing similarities.
ignore-comments=yes



# checks for:
#     * warning notes in the code like FIXME, XXX
#     * PEP 263: source code with non ascii character but no encoding declaration
#
[MISCELLANEOUS]
# Enable / disable this checker
enable-miscellaneous=yes

# List of note tags to take in consideration, separated by a comma. Default to
# FIXME, XXX, TODO
notes=FIXME,XXX,TODO



# checks for :
#     * unauthorized constructions
#     * strict indentation
#     * line length
#     * use of <> instead of !=
#
[FORMAT]
# Enable / disable this checker
enable-format=yes

# Maximum number of characters on a single line.
max-line-length=75

# Maximum number of lines in a module
max-module-lines=1000

# String used as indentation unit. This is usually " " (4 spaces) or "\t" (1 tab).
indent-string='    '

EOF

munge_in_place() {
    local file="$1"
    shift
    mv $file $file.in_place
    "$@" <$file.in_place >$file
    rm $file.in_place
}

# awk program to transform pylint output to one complete message per line.
cat >make_records.awk <<"EOF"
/^\*/ { package = $3; next }
       { print package ":" $0 }
EOF

# awk program to ignore lines matching a pattern
cat >ignore_pattern.awk <<"EOF"
#!/usr/bin/awk
BEGIN        { count = 0 }
$0 ~ pattern { count = count + 1; next }
             { print }
END          { if (count == 0) print "unmatched pattern:", pattern }
EOF

mkdir pylint.d
PYLINTRC=./pylintrc PYLINTHOME=pylint.d pylint $PYLINT_OPTS pdk >pylint.txt
PYLINTRC=./pylintrc PYLINTHOME=pylint.d pylint $PYLINT_OPTS picax >>pylint.txt

# stuff to check outside of the "pdk" directory
for extra in $(ls bin); do
    extra_name=$(echo $extra | sed 's/\.py//')
    ln -s bin/$extra bin_${extra_name}.py
    PYLINTRC=./pylintrc PYLINTHOME=pylint.d pylint $PYLINT_OPTS bin_${extra_name} >>pylint.txt
done

munge_in_place pylint.txt awk -f make_records.awk

ignore_message() {
    set +x
    local pattern="$1"

    munge_in_place pylint.txt \
        awk -f ignore_pattern.awk -v pattern="$pattern"
    set -x
}

ignore_message '^pdk.package:W0704:.*: Except doesn.t do anything'

ignore_message '^pdk.workspace:C0111:.*:semdiff:'
ignore_message '^pdk.workspace:W0302:'
ignore_message '^pdk.component:W0302:'
ignore_message '^pdk.component:E1101:.*:ComponentDescriptor.load'
ignore_message '^pdk.cache:W0104:.*:SimpleCache.import_from_framer'
ignore_message '^pdk.command_base:W0104:.*:add_cmpstr.__cmp__'
ignore_message '^pdk.command_base:W0104:.*:add_cmpstr.__str__'

ignore_message '^pdk.audit:E1101:.*:FactType.*__slots__'
ignore_message '^pdk.rules:C0111:.*evaluate.*'

ignore_message '^pdk.debish_condition:C0111:.*:DebishParser.parse_.*'
ignore_message '^pdk.debish_condition:W0631:.*:raw_debish_lex'

ignore_message '^pdk.version_control:W0704:.*:Git.iter_diff_files'
ignore_message '^pdk.channels:W0704:.*: Except'

ignore_message '^bin_utest:W0401'
ignore_message '^bin_utest:W0611'

ignore_message '^picax.*:C0111:.*:_'
ignore_message '^picax.*:C0111:.*:.*\\._'

ignore_message '^picax.unpack:W0122:.*:Package.run_script'
ignore_message '^picax.*:W0603:'
ignore_message '^picax.*:W0602:'
ignore_message '^picax.modules.debian-installer:C0103:'
ignore_message '^bin_picax-utest:C0103'
ignore_message '^picax.modules.*:R0401'
ignore_message '^picax.apt:E1101:.*:_get_latest_version'

# The picax script is temporary, so ignore its problems.

ignore_message '^bin_picax:'

# for unit tests only
ignore_message '^pdk.test..*:E1101:.*fail_'
ignore_message '^pdk.test..*:E1101:.*assert_'
ignore_message '^pdk.test..*:W0201:'
ignore_message '^pdk.test..*:W0704:'
ignore_message '^pdk.test..*:C0103:'
ignore_message '^pdk.test..*:C0111:'
ignore_message '^pdk.test.test_component:W0302:.*'
ignore_message "^pdk.test.test_debish_condition:E1101:\
.*:TestDebishCondition.test_marked_condition:"
ignore_message "^pdk.test.test_package:W0104:\
.*:TestPackageClass.test_emulation_behaviors:"
ignore_message "^pdk.test.test_package:E1101:\
.*:TestPackageClass.test_emulation_behaviors:"

cat pylint.txt
if [ $(wc -l <pylint.txt) != "0" ]; then
    fail 'pylint found errors.'
fi

# vim:set ai et sw=4 ts=4 tw=75:
