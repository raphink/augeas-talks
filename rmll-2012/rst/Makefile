MONO_FONT=Inconsolata
FONT=Eau
PRESENTATION=augeas-rmll-2012
PYGMENTS_STYLE=tango
ODP_TEMPLATE=/home/rpinson/Documents/template_presentation_5.otp
S5_TEMPLATE=ui/c2c

all: odp pdf s5

odp: $(PRESENTATION).odp

pdf: $(PRESENTATION).pdf

s5: $(PRESENTATION).html

%.odp: %.rst
	rst2odp --mono-font $(MONO_FONT) \
	  --font $(FONT) \
	  --template-file $(ODP_TEMPLATE) \
	  --pygments-style $(PYGMENTS_STYLE) \
	  $< $@

%.pdf: %.odp
	odp2pdf $<

%.html: %.rst
	python rst2s5.py \
	  --stylesheet=pygments.css \
	  --theme-url=$(S5_TEMPLATE) \
	  $< > $@

clean:
	rm -f *.odp *.pdf *.html
