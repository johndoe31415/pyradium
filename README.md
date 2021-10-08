# pyradium
[![Build Status](https://travis-ci.com/johndoe31415/pyradium.svg?branch=master)](https://travis-ci.com/johndoe31415/pyradium)

This is a complete rewrite of a presentation rendering tool I've originally
started in 2015. It is incorporating features of LaTeX-Beamer which I like into a renderer that outputs HTML. In particular, the design goals were:

  * Input the slide content in machine-readable form, no WYSIWYG. This is like
    latex-beamer, but I'm using XML as input files.
  * Have functionality like acronyms, automatic table of contents,
    cross-references, equations. This is also like LaTeX.
  * Output to a format that anyone can style: HTML and CSS. New slide templates
    should be easy to create (e.g., a three-column design or a "quote" slide
    template).
  * Use the advantages of HTML to provide new features, like instant feedback:
    I want people to tell me typos and general feedback about my presentation
    and want to make submission of that info as easy as possible (low entry
    barrier). Also it should record which git revsion was used to typeset the
    document so I know exactly if I've already fixed an issue or not if it gets
    reported multiple times.

## Name
pyradium has been previously known as pybeamer, but has been renamed because a
different project under that name exists on PyPi.

## Example
You can view an example of a presentation [here](https://johndoe31415.github.io/pyradium/).
The source for that presentation can be found [here](https://github.com/johndoe31415/pyradium/tree/master/examples).

## Usage
All features that have been mentioned above are implemented by pyradium. You
can see an example file in the [examples/ subdirectory](https://github.com/johndoe31415/pyradium/tree/master/examples).
XML namespaces are used to distinguish tags which are renderer commands, i.e.,
which have some special interpretation.  All other content is essentially pure
HTML.

## Display
You can view the presentation in a browser. Hitting "g" lets you goto a
specific slide while pressing "f" starts the full-screen view. Note that the
full-screen view uses [the CSS "zoom" property](https://caniuse.com/?search=zoom)
which is supported by pretty much every browser except for Firefox. On Firefox,
you can still full-screen a presentation but have to zoom manually in. There exists
a more than a decade old Firefox [issue for this](https://bugzilla.mozilla.org/show_bug.cgi?id=390936)
but it appears that this is deliberately not implemented.

## Third-Party Components
There are three external components that pyradium uses:

  * The default template "Antonio" is adapted from
    [Jimena Catalina at SlideCarnival](https://www.slidescarnival.com/antonio-free-presentation-template/84).
    It is licensed under CC-BY 4.0.
  * The font Fira Sans is included, from the [Google Fonts Project](https://fonts.google.com/specimen/Fira+Sans). 
    It is licensed under the OFL.
  * The font Latin Modern Mono is included, from [GUST](http://www.gust.org.pl/projects/e-foundry/latin-modern).
    It is licensed under the GUST font license.

All third party licenses can be found in the [licenses/ subdirectory](https://github.com/johndoe31415/pyradium/tree/master/licenses)
subdirectory. Additionally, detailed attribution information is also provided
as part of the template itself in the `configuration.json` file of the
respective template. For example, [this](https://github.com/johndoe31415/pyradium/blob/master/pyradium/templates/antonio/configuration.json)
is the configuration file of the "antonio" template.

## Simple Usage
First, you have to create a presentation. For this example, we'll use the
`example.xml` that is provided. Firstly, it needs to be rendered:

```
$ ./pyradium.py render -I examples/sub/ examples/example.xml rendered/
```

You'll notice that the `-I` parameter defines a subdirectory that is searched
for files. This is a feature of pyradium as well (it allows you to distribute
and organize large presentation into multiple files you can then combine into
one). Once it's rendered, you can create a web server to serve it:

```
$ ./pyradium.py serve rendered/
Serving: http://127.0.0.1:8123
```

Now simply redirect your browser there and enjoy the view.

## Complex Usage
There are of course more options to choose from. Read the help pages to learn more, for example:

```
$ ./pyradium.py render --help
usage: ./pyradium.py render [--image-max-dimension pixels]
                                            [-I path] [--template-dir path]
                                            [-t name] [-g width x height] [-r]
                                            [--collapse-animation]
                                            [-i filename]
                                            [-m {interactive,static}]
                                            [-F {timer}] [-l]
                                            [--re-render-watch path] [-f] [-v]
                                            [--help]
                                            infile outdir

Render a slide show

positional arguments:
  infile                Input XML file of the slide show.
  outdir                Output directory the presentation is put into.

optional arguments:
  --image-max-dimension pixels
                        When rendering imaages, specifies the maximum
                        dimension they're downsized to. The lower this value,
                        the smaller the output files and the lower the
                        quality. Defaults to 1920 pixels.
  -I path, --include-dir path
                        Specifies an additional include directory in which,
                        for example, images are located which are referenced
                        from the presentation. Can be issued multiple times.
  --template-dir path   Specifies an additional template directories in which
                        template style files are located. Can be issued
                        multiple times.
  -t name, --template-style name
                        Template style to use. Defaults to default.
  -g width x height, --geometry width x height
                        Slide geometry, in pixels. Defaults to 1280x720.
  -r, --remove-pauses   Ignore all pause directives and just render the final
                        slides.
  --collapse-animation  Do not render animations as multiple slides, just show
                        one complete slide.
  -i filename, --index-filename filename
                        Gives the name of the presentation index file.
                        Defaults to index.html. Useful if you want to render
                        multiple presentations in one subdirectory.
  -m {interactive,static}, --presentation-mode {interactive,static}
                        Generate this type of presentation. Can be one of
                        None, defaults to interactive.
  -F {timer}, --presentation-feature {timer}
                        Enable a specific presentation feature. Can be one of
                        None and can be given multiple times.
  -l, --re-render-loop  Stay in a continuous loop, re-rendering the
                        presentation if anything changes.
  --re-render-watch path
                        By default, all include files and the template
                        directory is being watched for changes. This option
                        gives additional files or directories upon change of
                        which the presentation should be re-rendered.
  -f, --force           Overwrite files in destination directory if they
                        already exist.
  -v, --verbose         Increase verbosity. Can be specified more than once.
  --help                Show this help page.
```


## License
pyradium is licensed under the GNU GPL-3.
