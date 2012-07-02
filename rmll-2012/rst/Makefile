MONO_FONT=Inconsolata
TEMPLATE_FILE=/home/rpinson/Documents/template_presentation_5.otp
PRESENTATION=augeas-rmll-2012

all: $(PRESENTATION).odp

%.odp: %.rst
	rst2odp --mono-font $(MONO_FONT) \
	  --template-file $(TEMPLATE_FILE) \
	  $< $@
