# -*- coding: utf-8 -*-

import os
import re
import codecs
import inspect
#import jinja2
import shutil
import tempfile

from subprocess import Popen
from six import string_types
from six.moves import configparser

#from . import utils
#from . import macro as macro_module
#from .parser import Parser


#BASE_DIR = os.path.dirname(__file__)
#THEMES_DIR = os.path.join(BASE_DIR, 'themes')
#TOC_MAX_LEVEL = 2
#VALID_LINENOS = ('no', 'inline', 'table')


class Converter(object):
    default_packages = ['listings', 'array', 'graphicx', 'lineno', 'dcolumn', 'bm', 'color', 'overpic', 'multirow', 'epstopdf']
    default_newcommands = []
    author = 'who?'
    title = 'what title?'
    dict_marks = {'#th ':'theme', '#pkg ':'package', '#nc ': 'newcommand', '#t ':'title', '# ':'title', '## ': 'frametitle', '#a ':'author', '#logo ': 'logo', '#date ': 'date',  '|':'table', '[]()':'figure', '- ':'item', '1. ':'enumerate' }
    content = []
    source_abspath = ''

    def __init__(self, source, **kwargs):
        """ Configures this converter. Available ``args`` are:
            - ``source``: source file or directory path
            Available ``kwargs`` are:
            - ``output_file``: path to html or PDF destination file
            - ``theme``: path to the theme to use for this presentation
        """
        self.output_file = kwargs.get('output_file', 'slides.tex')
        self.logger = kwargs.get('logger', None)
        self.theme = kwargs.get('theme', 'Warsaw')

        if not source or not os.path.exists(source) or not os.path.isfile(source):
            raise IOError(u"Source file %s does not exist"
                          % source)


        self.source = source
        source_abspath = os.path.abspath(source)

        if not os.path.isdir(source_abspath):
            source_abspath = os.path.dirname(source_abspath)

        self.source_abspath = source_abspath
        print 'source_abspath =', source_abspath

        if (os.path.exists(self.output_file)
            and not os.path.isfile(self.output_file)):
            raise IOError(u"Destination %s exists and is not a file"
                          % self.output_file)

        if self.output_file.endswith('.tex'):
            self.file_type = 'tex'
        elif self.output_file.endswith('.pdf'):
            self.file_type = 'pdf'
        else:
            raise IOError(u"This program can only write tex or pdf files. "
                           "Please use one of these file extensions in the "
                           "destination")



    #@property
    def get_attribute(self, line):
        for key in self.dict_marks:
            if key.startswith('#') or key.startswith('1.') or key.startswith('-'):
                if line.startswith(key):
                    line = line.replace(key, '').strip()
                    return line, self.dict_marks[key]
            elif key == '|':
                if line.startswith(key):
                    return line, self.dict_marks[key]
            else:
                flag = 1
                for i in key:
                    if i not in line:
                        flag = 0
                        break
                if flag == 1 and line.startswith(key[0]):
                    return line, self.dict_marks[key]
        return line, 'text'

    def update_basic_info(self, source):
        print 'it is doing update_basic_info'
        with open(source, 'r') as f0:
            while 1:
                line0 = f0.readline()
                if line0 == '' or line0.strip().startswith('---'):
                    break
                line0 = line0.strip()
                line0, attr = self.get_attribute(line0)
                if attr == 'theme' and line0 !='':
                    self.theme = line0
                elif attr == 'package':
                    line0 = line0.split(' ')
                    for p in line0:
                        if p in self.default_packages:
                            continue
                        self.default_packages.append(p)
                elif attr == 'newcommand':
                    line0 = line0.split(' ')
                    for nc in line0:
                        self.default_newcommands.append(nc)
                elif attr == 'author':
                    self.author = line0
                elif attr == 'title':
                    self.title = line0
                elif attr == 'logo':
                    self.logo = line0
                elif attr == 'date':
                    self.date = line0
                else:
                    continue

    def write_basic_info(self, source):
        print 'it is doing write_basic_info'
        self.update_basic_info(source)
        self.content.append('\\documentclass[10pt,reqno]{beamer} \n\n')
        for p in self.default_packages:
            self.content.append('\\usepackage{'+p+'} \n')
        self.content.append('\\usepackage[english]{babel} \n\n')
        for nc in self.default_newcommands:
            nc0 = nc.split('=')
            #print nc, nc0, nc0[0], nc0[1]
            self.content.append('\\newcommand{'+nc0[0]+'}{'+nc0[1]+'} \n')
        self.content.append('\n\\usetheme{'+self.theme+'} \n')
        self.content.append('\\setbeamertemplate{footline}[frame number]\n')
        self.content.append('\\begin{document} \n\n')
        self.content.append('\\begin{frame} \n\n')
        self.content.append('\\title{'+self.title+'}\n')
        self.content.append('\\author{'+self.author+'}\n')
        if 'nodate' in self.date:
            self.content.append('\\date{}\n')
        elif self.date != '':
            self.content.append('\\date{'+self.date+'}\n')
        self.content.append('\\titlepage\n\n')
        if self.logo != '':
                line = self.logo.strip()
                figure_size = line[line.find('[')+1:line.find(']')]
                figure_path = line[line.find('(')+1:line.find(')')]
                figure_tail = line[line.find(')')+1:len(line)]
                figure_width = ''
                figure_height = ''
                figure_size = figure_size.split(',')
                figure_width = 'width = '+figure_size[0]
                if 'mm' not in figure_size[0] and 'cm' not in figure_size[0]:
                    figure_width += '\\textwidth'
                if len(figure_size)>1:
                    figure_height = 'height = '+figure_size[1]
                    if 'mm' not in figure_size[1] and 'cm' not in figure_size[1]:
                        figure_height += '\\textheight'
                figure_size0 = figure_width
                if len(figure_size)>1:
                    figure_size0 += ', ' + figure_height
                list_logos = figure_path.split(',')
                self.content.append('\\center\n')
                for logo in list_logos:
                    self.content.append('\\includegraphics['+ figure_size0 +']{'+logo+'} '+figure_tail+'\n')
        self.content.append('\\end{frame}\n\n')

    def write_one_frame(self, lines):
        print 'it is doing write_one_frame'
        table_status = 0
        figure_status = 0
        item_status = 0
        enumerate_status = 0
        self.content.append('\\begin{frame} \n\n')
        for line0 in lines:
            line0, attr = self.get_attribute(line0.strip())
            #print line0, attr
            if attr == 'frametitle':
                line = line0.replace('## ', '')
                self.content.append('\\frametitle{'+line.strip()+'}\n\n')
            elif attr == 'table':
                table_status += 1
                line = line0.strip()
                line = line[1:len(line)-1]
                s = line.replace('|', '&')
                if s.strip()!='':
                    s += '\\\\ \n'
                line = line.split('|')
                tablealign = ''
                for i in range(len(line)):
                    tablealign += 'l'
                if table_status == 1:
                    self.content.append('\\begin{table}\\begin{tabular} {'+tablealign+'} \n \\hline\\hline \n')
                self.content.append(s)
                if table_status == 1:
                    self.content.append('\\hline\n')
            elif attr == 'figure':
                figure_status += 1
                line = line0.strip()
                figure_size = line[line.find('[')+1:line.find(']')]
                figure_path = line[line.find('(')+1:line.find(')')]
                figure_tail = line[line.find(')')+1:len(line)]
                figure_width = ''
                figure_height = ''
                figure_size = figure_size.split(',')
                figure_width = 'width = '+figure_size[0]
                if 'mm' not in figure_size[0] and 'cm' not in figure_size[0]:
                    figure_width += '\\textwidth'
                if len(figure_size)>1:
                    figure_height = 'height = '+figure_size[1]
                    if 'mm' not in figure_size[1] and 'cm' not in figure_size[1]:
                        figure_height += '\\textheight'
                figure_size0 = figure_width
                if len(figure_size)>1:
                    figure_size0 += ', ' + figure_height
                #if figure_status == 1:
                    #self.content.append('\\begin{figure}[htbp] \n')
                self.content.append('\\includegraphics['+ figure_size0 +']{'+figure_path+'} '+figure_tail+'\n')
            elif attr == 'item':
                if enumerate_status > 0:
                    enumerate_status = 0
                    self.content.append('\\end{enumerate} \n\n')
                item_status += 1
                line = line0.strip()
                if item_status == 1:
                    self.content.append('\\begin{itemize}\n')
                self.content.append('\\item '+line+'\n')
            elif attr == 'enumerate':
                enumerate_status += 1
                line = line0.strip()
                if enumerate_status == 1:
                    self.content.append('\\begin{enumerate}\n')
                self.content.append('\\item '+line+'\n')
            else:
                if table_status > 0:
                    table_status = 0
                    self.content.append('\\hline\\hline \n \\end{tabular}\\end{table} \n\n')
                if figure_status > 0:
                    figure_status = 0
                    #self.content.append('\\end{figure} \n\n')
                if enumerate_status > 0:
                    enumerate_status = 0
                    self.content.append('\\end{enumerate} \n\n')
                if item_status > 0:
                    item_status = 0
                    self.content.append('\\end{itemize} \n\n')
                line = line0.strip()
                self.content.append(line + '\n')
                #self.content.append(line + '\n\n')
        self.content.append('\n\n')
        self.content.append('\\end{frame} \n\n')

    def write_all_frames(self, source):
        print 'it is doing write_all_frame'
        print 'source =', source
        self.content = []
        self.write_basic_info(source)
        lines = []
        frame_status = 0
        with open(source, 'r') as f0:
            while 1 :
                line0 = f0.readline()
                print line0
                if line0 == '':
                    break
                if line0.startswith('---'):
                    frame_status += 1
                    if frame_status > 1:
                        self.write_one_frame(lines)
                        lines = []
                    continue
                if frame_status == 0:
                    continue
                else:
                    lines.append(line0)
        self.content.append('\\end{document}\n\n')


    def execute(self):
         self.write_and_log()


    def write_and_log(self):
        self.write()
        self.log(u"Generated file: %s" % self.output_file)


    def log(self, message, type='notice'):
        """ Logs a message (eventually, override to do something more clever).
        """
        if self.logger and not callable(self.logger):
            raise ValueError(u"Invalid logger set, must be a callable")
        if self.logger:
            self.logger(message, type)

    def write(self):
        """ Writes generated presentation code into the destination file.
        """
        source = self.source
        self.write_all_frames(source)
        if self.file_type == 'pdf':
            self.write_pdf()
        else:
            with open(self.output_file, 'w') as outfile:
                for a in self.content:
                    outfile.write(a)

    def write_pdf(self):
        """ Tries to write a PDF export from the command line using PrinceXML
            if available.
        """
        try:
            #f = tempfile.NamedTemporaryFile(delete=False, suffix='.tex')
            f = open(self.output_file.replace('.pdf', '.tex'), 'w')
            for a in self.content:
                f.write(a)
            f.close()
        except Exception:
            raise IOError(u"Unable to create temporary file, aborting")

        #dummy_fh = open(os.path.devnull, 'w')

        try:
            command = ["pdflatex", "-shell-escape", f.name]
            Popen(command).communicate()
        except Exception:
            raise EnvironmentError(u"Unable to generate PDF file using "
                                    "pdflatex. Is it installed and available?")
        finally:
            #dummy_fh.close()
            name = self.output_file.replace('.pdf', '')
            latex_trash = ['.out', '.log', '.aux', '.snm', '.nav', '.toc']
            for a in latex_trash:
                #print self.source_abspath+'/'+name+a
                if os.path.isfile(self.source_abspath+'/'+name+a):
                    os.remove(self.source_abspath+'/'+name+a)
