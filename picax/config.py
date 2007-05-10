# $Progeny$
#
# Load and manage configuration settings.
#
#   Copyright 2003, 2004, 2005, 2006 Progeny Linux Systems, Inc.
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

"""This module serves as the single source for all configuration
information for picax.  The underlying mechanisms for loading the
configuration should be completely hidden from the rest of the system."""

import sys
import os
import re
import xml.dom
import xml.dom.minidom

import picax.installer
import picax.media

config = {}

main_options = { "help":
                 { "config-key": "help",
                   "parameter": False,
                   "doc": ("Show brief usage help",) },
                 "debug":
                 { "config-key": "debug",
                   "parameter": False,
                   "doc": ("Turn debugging output on",) },
                 "quiet":
                 { "config-key": "quiet",
                   "parameter": False,
                   "doc": ("Suppress unneeded output",) },
                 "version":
                 { "config-key": "version",
                   "parameter": False,
                   "doc": ("Show the software version",) },
                 "order":
                 { "config-key": "order_file",
                   "parameter": True,
                   "parameter-desc": "file",
                   "doc": ("Set package order from file",) },
                 "arch":
                 { "config-key": "arch",
                   "parameter": True,
                   "parameter-desc": "architecture",
                   "doc": ("Target architecture",) },
                 "num-parts":
                 { "config-key": "num_parts",
                   "parameter": True,
                   "parameter-type": "number",
                   "parameter-default": 0,
                   "parameter-desc": "num",
                   "doc": ("Number of parts to split the repo into",) },
                 "part-size":
                 { "config-key": "part_size",
                   "parameter": True,
                   "parameter-type": "number",
                   "parameter-default": 0,
                   "parameter-desc": "bytes",
                   "doc": ("Size in bytes for each part",) },
                 "cd-label":
                 { "config-key": "cd_label",
                   "parameter": True,
                   "parameter-desc": "label",
                   "doc": ("Apt label for destination CD",) },
                 "dest-path":
                 { "config-key": "dest_path",
                   "parameter": True,
                   "parameter-desc": "path",
                   "doc": ("Destination for dirs/images",) },
                 "media":
                 { "config-key": "media_component",
                   "parameter": True,
                   "parameter-desc": "type",
                   "doc": ("Use the named media type",) },
                 "installer":
                 { "config-key": "installer_component",
                   "parameter": True,
                   "parameter-desc": "installer",
                   "doc": ("Use the named installer",) },
                 "source":
                 { "config-key": "source",
                   "parameter": True,
                   "parameter-default": "separate",
                   "parameter-constraints": [ "none", "separate",
                                              "immediate", "mixed" ],
                   "parameter-desc": "type",
                   "doc": ("Set type of source media to create",) },
                 "apt-repo-path":
                 { "config-key": "correction_apt_repo",
                   "parameter": True },
                 "short-package-list":
                 { "config-key": "short_package_list",
                   "parameter": False,
                   "doc":
                   ("Don't include all packages in the distribution",) },
                 "no-debootstrap":
                 { "config-key": "no_debootstrap",
                   "parameter": False,
                   "doc":
                   ("Don't automatically include debootstrap packages",) },
                 "base-media":
                 { "config-key": "base_media",
                   "parameter": True,
                   "parameter-type": "multistring",
                   "parameter-desc": "path[:path...]",
                   "doc": ("Paths to mounted media to use as base",)},
                 "read-config":
                 { "config-key": "input_config_path",
                   "parameter": True,
                   "parameter-desc": "filename",
                   "doc": ("Read configuration from file",)},
                 "write-config":
                 { "config-key": "output_config_path",
                   "parameter": True,
                   "parameter-desc": "filename",
                   "doc": ("Write configuration to file",)}}

module_prefixes = (("inst", "installer", "installer_options",
                    picax.installer.get_options),
                   ("media", "media", "media_options",
                    picax.media.get_options))

arch_identifiers = ((re.compile(r'i[3456]86'), "i386"),
                    (re.compile(r'x86_64'), "amd64"),
                    (re.compile(r'ia64'), "ia64"))

class ConfigError(StandardError):
    "Exception for flagging errors in configuration."
    pass

def _parse_value(option_dict, value, err_template):
    new_value = value.strip()

    if option_dict.has_key("parameter-type"):
        if option_dict["parameter-type"] == "number":
            new_value = int(new_value)
        elif option_dict["parameter-type"] == "multistring":
            new_value = new_value.split(":")
        else:
            raise ConfigError, \
                  "invalid parameter type '%s'" \
                  % (option_dict["parameter-type"],)

    if option_dict.has_key("parameter-constraints") and \
       new_value not in option_dict["parameter-constraints"]:
        raise ConfigError, err_template % (value,)

    return new_value

def _set_defaults(this_config, options):
    for option in options.keys():
        value = None
        if options[option]["parameter"]:
            if options[option].has_key("parameter-default"):
                value = options[option]["parameter-default"]
            elif options[option].has_key("parameter-type"):
                if options[option]["parameter-type"] == "multistring":
                    value = []
        else:
            value = False
        if value is not None:
            this_config[options[option]["config-key"]] = value

def _get_module_options(prefix):
    for mpinfo in module_prefixes:
        if mpinfo[0] == prefix:
            return mpinfo[3]()

    raise ValueError, "invalid prefix"

def _init():
    "Return a blank, initialized config dictionary."

    conf = { "repository_list": [],
               "debug": False }

    if os.environ.has_key("TMPDIR"):
        conf["temp_dir"] = os.environ["TMPDIR"]
    else:
        conf["temp_dir"] = "/tmp"

    if os.environ.has_key("PICAX_DEBUG"):
        conf["debug"] = True

    return conf

def _dom_to_config(this_config, topnode, options, prefixes = ()):
    for child in topnode.childNodes:
        if child.nodeType != xml.dom.Node.ELEMENT_NODE:
            continue

        module_options = None
        for prefixinfo in prefixes:
            if child.tagName == prefixinfo[2]:
                module_options = _get_module_options(prefixinfo[0])
                this_config[prefixinfo[2]] = _dom_to_config({}, child,
                                                            module_options)
                break
        if module_options is not None:
            continue

        if child.tagName == "repository":
            distro = child.getAttribute("distribution")
            comp = child.getAttribute("component")
            this_config["repository_list"].append((distro, comp))
            continue

        if child.tagName not in options.keys():
            raise ConfigError, "config file has invalid item: %s" \
                  % (child.tagName,)

        value = None
        if options[child.tagName]["parameter"]:
            for node in child.childNodes:
                if node.nodeType == xml.dom.Node.TEXT_NODE:
                    value = node.data
                    break
            if value is None:
                raise ConfigError, "config file item %s has no value" \
                      % (child.tagName,)

            message = "value %%s for config file item %s invalid" \
                        % (child.tagName,)
            value = _parse_value(options[child.tagName], value, message)
        else:
            value = True

        this_config[options[child.tagName]["config-key"]] = value

        if child.tagName == "installer":
            picax.installer.set_installer(value)
        elif child.tagName == "media":
            picax.media.set_media(value)

    return this_config

def _config_to_dom_tree(this_config, options, document, topnode,
                        prefixes = ()):
    option_list = options.keys()
    option_list.sort()
    for option in option_list:
        if option in ("read-config", "write-config"):
            continue
        if this_config.has_key(options[option]["config-key"]):
            value = this_config[options[option]["config-key"]]
            if options[option]["parameter"]:
                if options[option].has_key("parameter-type"):
                    if options[option]["parameter-type"] == "number":
                        value = str(value)
                    elif options[option]["parameter-type"] \
                            == "multistring":
                        value = ":".join(value)
                    else:
                        raise ConfigError, \
                              "invalid parameter type '%s'" \
                              % (options[option]["parameter-type"],)
                node = document.createElement(option)
                node.appendChild(document.createTextNode(value))
                topnode.appendChild(node)
            else:
                if value:
                    node = document.createElement(option)
                    topnode.appendChild(node)

    for prefixinfo in prefixes:
        prefix = prefixinfo[0]
        prefix_key = prefixinfo[2]
        if this_config.has_key(prefix_key):
            node = document.createElement(prefix_key)
            topnode.appendChild(node)
            suboptions = _get_module_options(prefix)
            _config_to_dom_tree(this_config[prefix_key], suboptions,
                                document, node)

    for (distro, comp) in this_config["repository_list"]:
        node = document.createElement("repository")
        node.setAttribute("distribution", distro)
        node.setAttribute("component", comp)
        topnode.appendChild(node)

def _config_to_dom(this_config, options, prefixes):
    document = xml.dom.minidom.parseString("<picaxconfig/>")

    _config_to_dom_tree(this_config, options, document,
                        document.documentElement, prefixes)

    return document

def _parse_args(this_config, arglist, options, sub_prefixes = ()):
    temp_arglist = arglist[:]
    subprefix_arglist = {}
    for subprefix in [x[0] for x in sub_prefixes]:
        subprefix_arglist[subprefix] = []

    try:
        while len(temp_arglist) > 0 and temp_arglist[0][0] == "-":
            arg = temp_arglist.pop(0)
            stripped_arg = arg
            while stripped_arg[0] == "-":
                stripped_arg = stripped_arg[1:]
            module_arg = ""
            for ch in stripped_arg:
                if ch == "-":
                    break
                else:
                    module_arg = module_arg + ch

            if stripped_arg.find("=") != -1:
                (stripped_arg, extra_arg) = stripped_arg.split("=", 1)
                arg = "--" + stripped_arg
                temp_arglist.insert(0, extra_arg)

            if stripped_arg in ("h", "?"):
                this_config["help"] = True
            elif options.has_key(stripped_arg):
                config_key = options[stripped_arg]["config-key"]
                has_value = options[stripped_arg]["parameter"]
                if has_value:
                    value = _parse_value(
                        options[stripped_arg], temp_arglist.pop(0),
                        "invalid value %%s for parameter --%s"
                        % (stripped_arg,))

                    this_config[config_key] = value
                else:
                    this_config[config_key] = True
            elif module_arg in [x[0] for x in sub_prefixes]:
                subprefix_arglist[module_arg].append(arg)
                if len(temp_arglist) > 0 and temp_arglist[0][0] != "-":
                    subprefix_arglist[module_arg].append(
                        temp_arglist.pop(0))
            else:
                raise ConfigError, "unknown option: " + arg

    except IndexError:
        raise ConfigError, "option requires value"

    return (temp_arglist, subprefix_arglist)

def _parse_component(this_config, component, options, sub_prefixes = ()):
    "Read configuration data from component metadata."

    std_prefix = "mediagen"
    submod_config = {}
    submod_list = [x[0] for x in sub_prefixes]

    # For PDK, we always write our media to the same place in the
    # workspace, so let's set an appropriate default.

    this_config["dest_path"] = os.getcwd() + "/images"

    # Separate out the media metadata.

    media_meta = dict([(x[1], component.meta[x])
                       for x in component.meta if x[0] == std_prefix])

    # Separate out the repository information, and save the rest
    # into the configuration dictionary.  At some point, we should
    # validate the configuration items against the options list.

    for metakey in media_meta:
        if "-" in metakey:
            submod = metakey.split("-", 1)[0]
        else:
            submod = None

        # Map "repository" specially, since we can't do attributes
        # in component metadata.

        if metakey == "repository":
            repo_strings = media_meta[metakey].split()
            for repo_string in repo_strings:
                (distro, section) = repo_string.split(':')
                this_config["repository_list"].append((distro, section))

        # Sub-module information.  Save it for _interpret_args,
        # and make it look like command-line arguments.

        elif submod and submod in submod_list:
            if submod not in submod_config:
                submod_config[submod] = []
            if media_meta[metakey]:
                submod_config[submod].append(
                    "--%s=%s" % (metakey, media_meta[metakey]))
            else:
                submod_config[submod].append("--" + metakey)

        # Everything else should just get configured.

        else:
            configkey = options[metakey]["config-key"]
            this_config[configkey] = media_meta[metakey]

    # Return "leftover arguments".  Here, this includes the submodules
    # lists and the path to the repository, which is always the repository
    # created by repogen.

    return ([os.getcwd() + "/repo"], submod_config)

def _interpret_args(this_config, subprefix_arglist, arglist):
    if os.environ.has_key("PICAX_DEBUG"):
        this_config["debug"] = True

    if this_config.has_key("installer_component"):
        picax.installer.set_installer(this_config["installer_component"])
    if this_config.has_key("media_component"):
        picax.media.set_media(this_config["media_component"])

    if this_config["help"]:
        optionlist = main_options
        for (mprefix, mname, mkey, mfunc) in module_prefixes:
            if this_config.has_key(mname + "_component"):
                optionlist = mfunc()
                break

        usage(sys.stdout, optionlist)
        sys.exit(0)
    elif this_config["version"]:
        version(sys.stdout)
        sys.exit(0)

    if len(arglist) not in (1, 3):
        raise ConfigError, "invalid repository arguments"

    if len(arglist) == 3:
        this_config["repository_list"].append(tuple(arglist[1:]))

    if len(this_config["repository_list"]) < 1:
        raise ConfigError, "no repositories provided"

    if this_config["num_parts"] == 0 and \
       this_config["part_size"] == 0 and \
       not this_config.has_key("media_component"):
        raise ConfigError, \
              "must specify media type, part size, or number of parts"
    if this_config["source"] == "separate" and \
       this_config["num_parts"] != 0:
        raise ConfigError, \
              "cannot use separate source and num_parts together"
    if this_config.has_key("media_component") and \
       (this_config["part_size"] != 0 or this_config["num_parts"] != 0):
        raise ConfigError, \
              "cannot set part size or number with a media module"

    new_repo_list = []
    for repo_item in this_config["repository_list"]:
        if repo_item not in new_repo_list:
            new_repo_list.append(repo_item)
    this_config["repository_list"] = new_repo_list

    this_config["base_path"] = arglist[0]
    this_config["base_path"] = os.path.abspath(this_config["base_path"])
    if not this_config.has_key("dest_path"):
        this_config["dest_path"] = this_config["base_path"]

    for (mprefix, mname, mkey, mfunc) in module_prefixes:
        if this_config.has_key(mname + "_component"):
            if not this_config.has_key(mkey):
                this_config[mkey] = {}
            module_options = mfunc()
            _set_defaults(this_config[mkey], module_options)
            if subprefix_arglist.has_key(mprefix):
                _parse_args(this_config[mkey], subprefix_arglist[mprefix],
                            module_options)
        else:
            if subprefix_arglist.has_key(mprefix) and \
               len(subprefix_arglist[mprefix]) > 0:
                raise ConfigError, \
                      "%s options given without %s" % (mname, mname)

    if this_config.has_key("order_file"):
        order_file = open(this_config["order_file"])
        try:
            order_lines = order_file.readlines()
            this_config["order_pkgs"] = [x.strip() for x in order_lines]
        finally:
            order_file.close()
    if not this_config.has_key("order_pkgs"):
        this_config["order_pkgs"] = []
    if this_config.has_key("media_component"):
        this_config["part_size"] = picax.media.get_part_size()

def get_config():
    "Retrieve the current configuration dictionary."

    global config

    if not config:
        raise RuntimeError, "configuration not initialized"

    return config

def version(out):
    "Return the version of picax."

    out.write("PICAX 2.0pre (svn revision: $Rev: 5513 $)\n")

def usage(out, options = None):
    "Print a usage statement to the given file."

    show_module_options = False
    if options is None:
        options = main_options
        show_module_options = True

    version(out)

    out.write("usage: %s [options] base-path [dist section]\n" \
              % (sys.argv[0],))
    out.write("  base-path: root URI for apt repository\n")
    out.write("  dist:      distribution name (such as 'woody')\n")
    out.write("  section:   component section name (such as 'main')\n")
    out.write("Options:\n")

    option_list = options.keys()
    option_list.sort()
    maxlen = 0
    option_strs = []
    for option in option_list:
        option_str = "  --%s" % (option,)
        if options[option]["parameter"]:
            if options[option].has_key("parameter-desc"):
                parameter_desc = options[option]["parameter-desc"]
            else:
                parameter_desc = "?"
            option_str = option_str + ("=<%s>" % (parameter_desc,))
        if len(option_str) > maxlen:
            maxlen = len(option_str)
        if options[option].has_key("doc"):
            doc_str = options[option]["doc"][0]
        else:
            doc_str = ""

        option_strs.append((option_str, doc_str))

    if show_module_options:
        option_strs.append(
            ("  --inst-<option>", "Pass an option to the installer"))
        option_strs.append(
            ("  --media-<option>", "Pass an option to the media handler"))

    if len(option_strs) < 1:
        out.write("  No options are supported by this module.\n")
    else:
        maxlen = maxlen + 2
        for (option_str, option_doc) in option_strs:
            while len(option_str) < maxlen:
                option_str = option_str + " "
            out.write(option_str + option_doc + "\n")

def handle_args(arglist = None, component = None):
    "Parse the argument list and store the initial configuration."

    global config
    global main_options
    global module_prefixes

    if arglist is None and component is None:
        raise ValueError, "handle_args not given a proper config source"
    if arglist is not None and component is not None:
        raise ValueError, \
              "handle_args must only receive a single config source"

    # Initialize the global config dictionary.

    config = _init()
    _set_defaults(config, main_options)

    # Read the configuration from the proper source(s), whatever they
    # may be.

    if arglist is not None:

        # Command line parsing.  This is made slightly more complicated
        # because there are multiple configuration sources, with priority:
        # command line trumps saved XML configuration.  So, we have to
        # load the two configuration sources into separate dictionaries,
        # and merge them in the proper order.

        cmdline_config = _init()
        xml_config = cmdline_config.copy()

        (remaining, subprefix_arglist) = _parse_args(cmdline_config,
                                                     arglist,
                                                     main_options,
                                                     module_prefixes)

        if cmdline_config.has_key("input_config_path"):
            try:
                document = xml.dom.minidom.parse(
                    cmdline_config["input_config_path"])
            except:
                raise ConfigError, "cannot parse XML configuration file"
            xml_config = _dom_to_config(xml_config,
                                        document.documentElement,
                                        main_options, module_prefixes)
            config.update(xml_config)

        for config_key in cmdline_config.keys():
            if config_key not in [x[2] for x in module_prefixes]:
                config[config_key] = cmdline_config[config_key]
    else:

        # Component configuration.  Simple, because there's only
        # one source for configuration.

        (remaining, subprefix_arglist) = _parse_component(config,
                                                          component,
                                                          main_options,
                                                          module_prefixes)

    # Do some interpretation and sanity-checking of the configuration.

    _interpret_args(config, subprefix_arglist, remaining)

    # Command-line configuration allows for the current configuration
    # to be saved to an XML file.  Do that now if we need to.

    if arglist is not None and config.has_key("output_config_path"):
        document = _config_to_dom(config, main_options, module_prefixes)
        outfile = open(config["output_config_path"], "w")
        outfile.write(document.toprettyxml("    "))
        outfile.close()

    # Handle architecture after writing the default, so the arch
    # doesn't show up in the configuration unless explicitly added.

    if not config.has_key("arch"):
        arch_f = os.popen("uname -a")
        arch_data = arch_f.read()
        arch_f.close()

        for (arch_re, arch_id) in arch_identifiers:
            if arch_re.search(arch_data):
                config["arch"] = arch_id
                break

# vim:set ai et sw=4 ts=4 tw=75:
