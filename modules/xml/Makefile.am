module_LTLIBRARIES      += modules/xml/libxml.la
modules_xml_libxml_la_SOURCES = \
  modules/xml/xml-grammar.y       \
  modules/xml/xml-parser.c        \
  modules/xml/xml-parser.h        \
  modules/xml/xml-plugin.c        \
  modules/xml/xml.h               \
  modules/xml/xml.c               \
  modules/xml/xml-private.h       \
  modules/xml/windows-eventlog-xml-parser.h \
  modules/xml/windows-eventlog-xml-parser.c \
  modules/xml/filterx-parse-xml.h \
  modules/xml/filterx-parse-xml.c \
  modules/xml/filterx-parse-windows-eventlog-xml.h \
  modules/xml/filterx-parse-windows-eventlog-xml.c \
  modules/xml/filterx-func-format-xml.h \
  modules/xml/filterx-func-format-xml.c \
  modules/xml/filterx-func-format-windows-eventlog-xml.h \
  modules/xml/filterx-func-format-windows-eventlog-xml.c



BUILT_SOURCES       +=      \
  modules/xml/xml-grammar.y       \
  modules/xml/xml-grammar.c       \
  modules/xml/xml-grammar.h

EXTRA_DIST        +=      \
  modules/xml/xml-grammar.ym	\
  modules/xml/CMakeLists.txt

modules_xml_libxml_la_CPPFLAGS  =     \
  $(AM_CPPFLAGS)            \
  -I$(top_srcdir)/modules/xml        \
  -I$(top_builddir)/modules/xml
modules_xml_libxml_la_LIBADD  = $(MODULE_DEPS_LIBS)
modules_xml_libxml_la_LDFLAGS = $(MODULE_LDFLAGS)
EXTRA_modules_xml_libxml_la_DEPENDENCIES= $(MODULE_DEPS_LIBS)

modules/xml modules/xml/ mod-xml: modules/xml/libxml.la
.PHONY: modules/xml/ mod-xml

include modules/xml/tests/Makefile.am
