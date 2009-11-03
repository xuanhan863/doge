"""
Python docstring generator.
"""
__docformat__ = "restructuredtext en"

## Copyright (c) 2009 Emmanuel Goossaert 
##
## This file is part of pydoge.
##
## pydoge is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## pydoge is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with pydoge.  If not, see <http://www.gnu.org/licenses/>.



import re
import doc
import python_pattern

#from doc import SBSection



class RestructuredTextWriter:

    def __init__(self):
        pass

    def make_docstring(self, node):
        for section in node.sf:
            pass


    def start(self, padding, content):
        if not content:
            return ''
        ret = '\n' if len(content) > 1 else ''
        return padding.padding(0) + '"""' + ret
              

    def end(self, padding, content):
        if not content:
            return ''
        return padding.padding(0) + '"""' + '\n'


    def make_docstring_list(self, sb, list):
        docstring = []
        #list = list[:] # local copy
        for name in list:
            # TODO replace the list in SB by a dictionary: for SB with no name,
            # take the len of the dict at the moment of the add
            
            for section in sb.sd:
                name_section = getattr(section, 'name', None)
                if name_section and name_section == name:
                    docstring.append(section.make_docstring())

        return '\n'.join(docstring)


    def make_docstring_not_list(self, sb, list):
        docstring = []
        for section in sb.sd:
            name_section = getattr(section, 'name', None)
            if not name_section or name_section not in list:
                #docstring.append(section.make_docstring(name_section))
                docstring.append(section.make_docstring())

        return '\n'.join(docstring)


    def make_docstring_sorted(self, sb, sections_start=[], sections_end=[], sections_exclude=[]):
        ds_start = self.make_docstring_list(sb, sections_start)
        ds_middle = self.make_docstring_not_list(sb, sections_start + sections_end + sections_exclude)
        ds_end = self.make_docstring_list(sb, sections_end)
        #print 'make', priority, non_priority

        newline_start = '\n' if ds_start and ds_middle else ''
        newline_middle = '\n' if ds_end and (ds_start or ds_middle) else ''

        return ds_start + newline_start + ds_middle + newline_middle + ds_end


    def make_docstring_file(self, sb):
        # TODO make sure the parameters are detected, or fix the code that handles parent/class nodes.
        sections_start = ['*Short', '*Long', 'Parameters']
        sections_exclude = ['Types']
        return self.make_docstring_sorted(sb, sections_start, [], sections_exclude)


    def make_docstring_class(self, sb):
        sections_start = ['*Short', '*Long', 'IVariables', 'CVariables']
        sections_exclude = ['Types']
        return self.make_docstring_sorted(sb, sections_start, [], sections_exclude)


    def make_docstring_function(self, sb):
        sections_start = ['*Short', '*Long', 'Parameters', 'Exceptions']
        sections_end = ['Return', 'ReturnType']
        sections_exclude = ['Types']
        return self.make_docstring_sorted(sb, sections_start, sections_end, sections_exclude)


    def _cut_line(self, line, len_editable):
        words = re.split('\s', line)
        id_cut = 0
        if len(words[0]) >= len_editable:
            # first word bigger than the line: can't cut it!
            id_cut = 1
        else :
            # else, let's decompose the line
            len_cut = 0
            while len_cut < len_editable:
                id_cut += 1
                len_cut = len(' '.join(words[:id_cut]))
            id_cut -= 1

        return words[:id_cut], words[id_cut:] 


    # TODO: is this function used somewhere?
    def _format_lines(self, lines, len_indent, len_max=80):
        formatted = []
        len_editable = len_max - len_indent
        if len_editable <= 0:
            return lines
        
        for line in lines:
            indexes = [(pos * len_editable, (pos + 1) * len_editable) for pos in range((len(lines) // len_editable) + 1)]
            for index in indexes:
                start = index(0)
                end = index(1)
                formatted.append(' ' * len_indent + line[start, end])
                

    #def _make_docstring_description(self, node):
    #    doc_description = '%s%s\n'.replace(' ','')
    #    description_short = [doc_description % (indent, line) for line in node.descriptions[0]]
    #    description_long = [doc_description % (indent, line) for line in node.descriptions[1]]


    #def _make_docstring_parameters(self, node, parameters):
    #    doc_parameter = '%s%s\n\
    #                    %s%s\n'.replace(' ','')
    #    return [doc_parameter % (indent_name, name, indent_description, ''.join(description)) for name, description in parameters.items()]



    def make_docstring_text_sb(self, section, level_indent):
        newline = '\n' if not section.text or not section.text[-1].endswith('\n') else ''
        if section.text == None:
            section.text = []
        #return '\n'.join(section.padding.padding(level_indent) + line for line in section.text) + newline
        return '\n'.join(self._format_text(line, len(section.padding.padding(level_indent)), 80) for line in section.text) + newline


    def _format_text(self, text, indent, size):
        # get the position of all the spaces in the given text
        positions_space = [index + 1 for index, char in enumerate(text) if char == ' ']

        positions_cut = []
        index_start = 0
        index_end = 0
        index_current = 0
        while index_current < len(positions_space):
            position = positions_space[index_current]
            if position <= positions_space[index_start] + size - indent:
                # The current space is still in the limit
                index_end = index_current
                index_current += 1
            else:
                # The current space has been found after the formatting limit
                # therefore a cut has to be done here
                positions_cut.append(positions_space[index_end])  
                index_start = index_end + 1
        
        # Starting and ending positions are added, and sequence pairs are computed
        positions_cut = [0] + positions_cut + [len(text)]
        limits = [(first, second) for first, second in zip(positions_cut[:-1], positions_cut[1:])]

        # The lines are constructed with valid indentation, jointed and returned
        lines = [' ' * indent + text[limit[0]:limit[1]].strip() for limit in limits] 
        return '\n'.join(lines)


    def make_docstring_description_sb(self, sb):
        title = sb.padding.padding(0) + ':' + sb.name + ':\n' if not sb.name.startswith('*') else ''
        level = 0 if sb.name.startswith('*') else 1
        return title + '\n'.join(self.make_docstring_text_sb(s, level_indent=level) for s in sb.sd)

    
    def make_docstring_parameters_sb(self, sb):
        doc_parameter = '%s\n\
                         %s'.replace(' ','')
                         #%s--\n'.replace(' ','')
        buffer = [sb.padding.padding(0) + ':' + sb.name + ':\n'] if sb.parameters else []
        for parameter in sb.parameters.values():
            name = parameter.name
            type = parameter.type
            doc_title = '%(indent)s%(name)s : %(type)s' if type else '%(indent)s%(name)s'
            title = doc_title % {'name': name, 'type': type, 'indent': sb.padding.padding(1)}

            text = ''.join([self.make_docstring_text_sb(s, level_indent=2) for s in parameter.sd])
            newline = '\n' if not text or (text and text[-1] != '\n') else ''
            #newline = '\n' if not text else ''
            #newline = ''
            #for s in parameter.sd:
            #    for line in s.text:
            #        print 'formatted', self._format_text(line.strip(), len(sb.padding.padding(2)), 80)


            docstring = doc_parameter % (title, text + newline)
            buffer.append(docstring)
        return ''.join(buffer)# + '--\n'

        #return [doc_parameter % (indent_name, name, indent_description, ''.join(description)) for name, description in section.parameters.items()]
