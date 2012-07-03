MONO_FONT=Inconsolata
TEMPLATE_FILE=/home/rpinson/Documents/template_presentation_5.otp
PRESENTATION=augeas-rmll-2012

all: pdf

odp: $(PRESENTATION).odp

pdf: $(PRESENTATION).pdf

%.odp: %.rst
	rst2odp --mono-font $(MONO_FONT) \
	  --template-file $(TEMPLATE_FILE) \
	  $< $@

%.pdf: %.odp
	odp2pdf $<

clean:
	rm -f *.odp *.pdf
