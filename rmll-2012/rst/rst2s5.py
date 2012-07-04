# -*- coding: utf-8 -*-
"""
    The Pygments reStructuredText directive
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Docutils_ 0.5 directive that renders source code
    (to HTML only, currently) via Pygments.

    To use it, adjust the options below and copy the code into a module
    that you import on initialization.  The code then automatically
    registers a ``code-block`` directive that you can use instead of
    normal code blocks like this::

        .. code-block:: python

            My code goes here.

    If you want to have different code styles, e.g. one with line numbers
    and one without, add formatters with their names in the VARIANTS dict
    below.  You can invoke them instead of the DEFAULT one by using a
    directive option::

        .. code-block:: python
            :linenos:

            My code goes here.

    Look at the `directive documentation`_ to get all the gory details.

    .. _Docutils: http://docutils.sf.net/
    .. _directive documentation:
       http://docutils.sourceforge.net/docs/howto/rst-directives.html

    :copyright: Copyright 2006-2009 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = False
PYGMENTS_STYLE = "fruity" # default

from pygments.formatters import HtmlFormatter

# The default formatter
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES, style=PYGMENTS_STYLE)

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    # 'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
}


from docutils import nodes, SettingsSpec
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

class Pygments(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        # take an arbitrary option if more than one is given
        formatter = self.options and VARIANTS[self.options.keys()[0]] or DEFAULT

        print >>open('pygments.css', 'w'), formatter.get_style_defs('.highlight')
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('code-block', Pygments)

class SetSlideDesign(Directive):
    """For compatibility with rst2odp
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    def run(self):
        return []

directives.register_directive('slide-design', SetSlideDesign)

from docutils.core import publish_cmdline, default_description

description = ('Generates S5 (X)HTML slideshow documents from standalone '
               'reStructuredText sources.  ' + default_description)

settings_spec = SettingsSpec()
settings_spec.settings_spec = (
    'S5 Wrapper Specific Options', # option group title
    None, # Description
    ( # options (help string, list of options, dictions of OptionParser.add_option dists)
        ('Specify a Pygments style (see pygmentize -L styles)',
	 ['--pygments-style'],
	 {'action': 'store',
          'dest': 'pygments_style'}),
    )
  )

publish_cmdline(writer_name='s5', description=description, settings_spec=settings_spec)

