AUTHORS="Kjetil Olsen Lye @ ETHZ <kjetil.o.lye@gmail.com> and Deep Ray @ EPFL <deep.ray@epfl.ch>"
import numpy
import os
import glob
import sys

import matplotlib
matplotlib.rcParams['savefig.dpi']=300
from numpy import *
import matplotlib.pyplot as plt

import tikzplotlib
import PIL
import socket
import os
import os.path
import datetime
import traceback
import inspect
import copy
try:
    from IPython.core.display import display, HTML
except:
    def display(x):
        print(x)

    def HTML(x):
        return x

import git
def get_git_metadata():
    if not get_git_metadata.cached:
        get_git_metadata.repo = git.Repo(search_parent_directories=True)
        get_git_metadata.sha = get_git_metadata.repo.head.object.hexsha
        get_git_metadata.modified= get_git_metadata.repo.is_dirty()
        get_git_metadata.activeBranch = get_git_metadata.repo.active_branch
        get_git_metadata.url = get_git_metadata.repo.remotes.origin.url
        get_git_metadata.cached = True
        get_git_metadata.short_sha = get_git_metadata.repo.git.rev_parse(get_git_metadata.sha, short=1)

    return {'git_commit': str(get_git_metadata.sha),
                'git_repo_modified':str(get_git_metadata.modified),
                'git_branch' : str(get_git_metadata.activeBranch),
                'git_remote_url' : str(get_git_metadata.url),
                'git_short_commit' : str(get_git_metadata.short_sha)}

get_git_metadata.cached = False


def add_git_information(filename):
    writeMetadata(filename, get_git_metadata())


def get_stacktrace_str():
    trace = ""
    for k in inspect.stack()[1:]:
        trace +=  "[function: {}, line: {}, file: {}]\n".format(k.function, k.lineno, k.filename)
    return trace


def get_loaded_python_modules():
    module_names = sys.modules.keys()

    modules_dictionaries = []

    for module_name in module_names:
        version = "Unknown"
        name = str(module_name)
        file = "Unknown"
        module = sys.modules[module_name]
        try:
            version = str(module.__version__)

        except:
            pass

        try:
            name = str(module.__name__)
        except:
            pass

        try:
            file = str(module.__file__)
        except:
            pass

        modules_dictionaries.append({"name" : name, "version": version, "file": file})

    return modules_dictionaries


def get_loaded_python_modules_formatted():
    module_list = get_loaded_python_modules()
    s = ""
    for m in module_list:
        s += "{name}: {version} ({file})\n".format(**m)

    return s

def get_python_description():
    return "{} (Version: {})".format(sys.executable, sys.version)

# From https://stackoverflow.com/a/6796752
class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


class RedirectStdStreamsToNull(object):
    def __init__(self):
        self._devnull = open(os.devnull, 'w')
        self._redirect_stream = RedirectStdStreams(self._devnull, self._devnull)

    def __enter__(self):
        self._redirect_stream.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self._redirect_stream.__exit__(exc_type, exc_value, traceback)
        self._devnull.close()





def writeMetadata(filename, data):
    im = PIL.Image.open(filename)

    meta = PIL.PngImagePlugin.PngInfo()

    for key in data.keys():
        meta.add_text(key, str(data[key]))
    im.save(filename, "png", pnginfo=meta)

def only_alphanum(s):
    return ''.join(ch for ch in s if ch.isalnum() or ch =='_')

def get_current_title():
    try:
        title = plt.gca().get_title()
        if title is not None and title.strip() !="":
            return title
    except:
        pass

    try:
        title = plt.gcf()._suptitle.get_text()
        print(title)
        if title is not None and title.strip() != "":
            return copy.deepcopy(title)
    except:
        pass
    try:
        print()
        return copy.deepcopy(plt.gcf().texts[0].get_text())
    except:
        return ''

def savePlot(name):
    for folder in ['img', 'img_tikz']:
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    original_name = copy.deepcopy(name)
    if savePlot.disabled:
        return




    name = showAndSave.prefix + name
    name = ''.join(ch for ch in name if ch.isalnum() or ch =='_')
    name = name.lower()


    if not name.endswith("_notitle"):
        old_title = get_current_title()
        title = old_title
    else:
        title = "None"

    fig = plt.gcf()
    ax = plt.gca()
    gitMetadata = get_git_metadata()
    informationText = 'By %s\nCommit: %s\nRepo: %s\nHostname: %s' % (AUTHORS, gitMetadata['git_commit'], gitMetadata['git_remote_url'], socket.gethostname())
    textcolor='gray'

    # we also have some 3d plots, which we need to use a special text function,
    # see https://matplotlib.org/examples/mplot3d/text3d_demo.html
    if '3d' in ax.name:
        text_function = ax.text2D
    else:
        text_function = ax.text
    try:
        
        text_function(0.95, 0.01, informationText,
                fontsize=3, color=textcolor,
                ha='right', va='bottom', alpha=0.5, transform=ax.transAxes)
    except:
        # This doesn't always work for 3d plots
        pass

    if gitMetadata['git_short_commit'] != "unkown":
        try:
            if not name.endswith("_notitle"):
                text_function(0.2, 0.93, "@" + gitMetadata['git_short_commit'], fontsize=10,
                              ha='right', va='bottom', color=textcolor, alpha=0.5, transform=ax.transAxes)
        except:
            # 3d plots had some issues with the text attribute
            pass
    # We don't want all the output from tikzplotlib

    with RedirectStdStreamsToNull():
        if savePlot.saveTikz:
            try:
                tikzplotlib.save('img_tikz/' + name + '.xyz',
                                     figureheight = '\\figureheight',
                                     figurewidth = '\\figurewidth',
                                     show_info = False)

                with open ('img_tikz/' + name + '.xyz', 'a') as f:
                    f.write("\n\n")
                    f.write("%% INCLUDE THE COMMENTS AT THE END WHEN COPYING\n")
                    f.write("%%%%%%%%%%%%%TITLE%%%%%%%%%%%%%%%%%\n")
                    for line in title.splitlines():
                        f.write("%% {}\n".format(line))
                    f.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
                    f.write("%% script name: {}".format(get_notebook_name()))
                    f.write("\n")
                    f.write("%% ALWAYS INCLUDE THE COMMENTS WHEN COPYING THIS PLOT\n")
                    f.write("%% DO NOT REMOVE THE COMMENTS BELOW!\n")
                    for k in gitMetadata.keys():
                        f.write("%% GIT {} : {}\n".format(k, gitMetadata[k]))

                    f.write("%% working_directory : {}\n".format(os.getcwd()))
                    f.write("%% hostname : {}\n".format(socket.gethostname()))
                    f.write("%% generated_on_date : {}\n".format(str(datetime.datetime.now())))
                    f.write("%% accessed_environment:\n")
                    for k in get_environment.accessed_environments.keys():
                        environment_value = get_environment.accessed_environments[k]
                        environment_value = environment_value.replace("\n", "")
                        environment_value = environment_value.replace("\r", "")
                        f.write("%%    {}={}\n".format(k, environment_value))
                    f.write("%% additional_parameters:\n")

                    for k in get_additional_plot_parameters():
                        environment_value = get_additional_plot_parameters()[k]
                        environment_value = environment_value.replace("\n", "")
                        environment_value = environment_value.replace("\r", "")
                        f.write("%%    {}={}\n".format(k, environment_value))

                    f.write("%% python_version: \n")
                    for l in get_python_description().splitlines():
                        f.write("%%    {}\n".format(l))

                    f.write("%% python modules:\n")
                    for module in get_loaded_python_modules():
                        f.write("%%     {name}: {version} ({file})\n".format(**module))

                    f.write("%% stacktrace:\n")
                    for line in get_stacktrace_str().splitlines():
                        f.write("%%     {}\n".format(line))
            except:
                console_log("Failed to save tikz file {}.xyz (probably just a 3d plot, they do not work in tikz)".format(name))




    savenamepng = 'img/' + name + '.png'
    plt.savefig(savenamepng, bbox_inches='tight')

    writeMetadata(savenamepng, {'Copyright' : 'Copyright, {}'.format(AUTHORS),
                               'working_directory': os.getcwd(),
                                'hostname':socket.gethostname(),
                                'generated_on_date': str(datetime.datetime.now()),
                                **gitMetadata,
                                **get_environment.accessed_environments,
                                **get_additional_plot_parameters(),
                                "modules_loaded": get_loaded_python_modules_formatted(),
                                "python_version": get_python_description(),
                                'stacktrace': get_stacktrace_str(),
                                'in_file' : get_notebook_name()})

    if savePlot.callback is not None:
        title = 'Unknown title'
        try:
            title = plt.gcf()._suptitle.get_text()
        except:
            pass
        savePlot.callback(savenamepng, name, title)

    if not name.endswith("_notitle"):
        old_title = get_current_title()
        plt.title("")
        savePlot(original_name + "_notitle")
        plt.title(old_title)
        title = old_title
    else:
        title = "None"

savePlot.callback = None
savePlot.saveTikz = True

def showAndSave(name):
    savePlot(name)
    if not showAndSave.silent:
        plt.show()
    plt.close()

showAndSave.prefix=''
showAndSave.silent=False

savePlot.disabled = False


def legendLeft():
    ax = plt.gca()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

import inspect
def console_log_show(x):
    try:
        x = "{} (in {}): {}".format(str(datetime.datetime.now()), inspect.stack()[1][3], x)
    except:
        x = "{} (in unknown function): {}".format(str(datetime.datetime.now()), x)
    console_log(x)
    print(x)
def isnotebook():
    # see  https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter
def console_log(x):
    """Simple hack to write to stdout from a notebook"""

    x=str(x)

    if isnotebook():
        with open('/dev/stdout', 'w') as f:
            f.write("DEBUG: %s\n"%x)
            f.flush()
    else:
        print(x)

def to_percent(y, position):
    # see https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
    s = "{:.1f}".format(y*100)

    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'%\%$'
    else:
        return s + '%'



def set_percentage_ticks(ax):
    """ ax is either plt.gca().xaxis or plt.gca().yaxis"""
    ax.set_major_formatter(matplotlib.ticker.FuncFormatter(to_percent))

def get_environment(name, filenames):
    """
    Gets the environment variable "name" and checks that the
    folder os.environ[name]/filename exists for each filename in filenames
    """
    if name not in os.environ:
        raise Exception("Environment variable {name} not set.".format(name=name))

    basepath = os.environ[name]
    for f in filenames:
        if not os.path.exists(os.path.join(basepath, f)):
            raise Exception(("Environment variable {name} is set to {basepath},\n " +\
                           "but {fullpath} does not exists.").format(name=name,
                                                                    basepath=basepath,
                                                                    fullpath=os.path.join(basepath, f)))
    get_environment.accessed_environments[name] = basepath
    return basepath


get_environment.accessed_environments = {}

def add_additional_plot_parameters(parameter, name):
    add_additional_plot_parameters.par_name[parameter] =  name
    
def get_additional_plot_parameters():
    return add_additional_plot_parameters.par_name

add_additional_plot_parameters.par_name = {}

    
def get_notebook_name():
    return get_notebook_name.name

get_notebook_name.name = sys.argv[0]

def set_notebook_name(name):
    get_notebook_name.name = name
