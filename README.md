# pyradium
[![Build Status](https://travis-ci.com/johndoe31415/pyradium.svg?branch=master)](https://travis-ci.com/johndoe31415/pyradium)

This is a tool which takes XML input that describes a presentation and renders
it into a presentation HTML. It borrows ideas from LaTeX-beamer but also
combines the flexible way of creating visually appealing documents using
HTML/CSS. it In particular, the features are:

  * Input the slide content in machine-readable form, no WYSIWYG. This is like
    LaTeX-beamer, but pyradium uses XML as input format. This allows for
    version controlled presentation input data as well.
  * Acronyms, automatic table of contents, cross-references, LaTeX equations
    are all supported.
  * Delegation of scripts that generate content for inclusion. For example, a
    'crypto helper' can be programmed as an external script that allows writing
    slides that only specify input data, cipher and key. Then the ciphertext is
    automatically computed and errors on the slides are avoided.
  * Syntax highlighting of code or terminal output (using pygments).
  * Output is easily customizable: HTML and CSS are used as the underlying
    technologies. Creation of new slide templates is simple (e.g., a
    three-column design or a "quote" slide template).
  * Use the advantages of HTML and ECMAScript to provide features like
    presentation feedback: Make it easy for people to report typos and general
    feedback about the presentation.  Make submission of that info as easy as
    possible (low entry barrier). Also it records which git revsion was used to
    typeset the document so I know exactly if I've already fixed an issue or not if
    it gets reported multiple times.

## Installation
pyradium is available on PyPi, so installation is as easy as

```
$ pip3 install pyradium
```

## History
pyradium has been previously known as pybeamer (in reference to LaTeX-beamer),
but has been renamed because a different project under that name exists on
PyPi. It started out as pybeamer in 2015 as a pet project of mine that I've
never published, but it has since been completely rewritten.

## Example
You can view an example of a presentation [here](https://johndoe31415.github.io/pyradium/).
The source for that presentation can be found [here](https://github.com/johndoe31415/pyradium/tree/master/examples).

## Input Documents
You can see an example XML file in the [examples/
subdirectory](https://github.com/johndoe31415/pyradium/tree/master/examples).
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
There are of course more options to choose from. Read the help pages to learn
more. To get an overview over the available facilities:

```
$ ./pyradium.py --help
usage: ./pyradium.py [command] [options]

HTML presentation renderer

Available commands:
    render             Render a presentation
    showstyleopts      Show all options a specific style permits
    serve              Serve a rendered presentation over HTTP
    acrosort           Sort an acryonym database
    purge              Purge the document cache
    hash               Create a hash of a presentation and all dependencies to
                       detect modifications
    dumpmeta           Dump the metadata dictionary in JSON format
    spellcheck         Spellcheck an XML presentation file
    dictadd            Add false-positive spellcheck errors to the dictionary

version: pyradium v0.0.6rc0

Options vary from command to command. To receive further info, type
    ./pyradium.py [command] --help
```

Each facility has its own help page. The `render` facility, for example:

```
$ ./pyradium.py render --help
usage: ./pyradium.py render [--image-max-dimension pixels] [-I path]
                            [-R path:uripath] [--template-dir path] [-t name]
                            [-o key=value] [-g width x height] [-r]
                            [--collapse-animation] [-i filename] [-j filename]
                            [-e {interactive,timer,info,pygments,acronyms}]
                            [-d {interactive,timer,info,pygments,acronyms}]
                            [-l] [--re-render-watch path] [-f] [-v] [--help]
                            infile outdir

Render a presentation

positional arguments:
  infile                Input XML file of the presentation.
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
  -R path:uripath, --resource-dir path:uripath
                        Specifies the resource directory both as the actual
                        deployment directory and the URI it has when serving
                        the presentation. By default, the deployment directory
                        of resources is identical to the output directory and
                        the uripath is '.'.
  --template-dir path   Specifies an additional template directories in which
                        template style files are located. Can be issued
                        multiple times.
  -t name, --template-style name
                        Template style to use. Defaults to antonio.
  -o key=value, --style-option key=value
                        Pass template-style specific options to the renderer.
                        Must always be in the form of "key=value", but what
                        keys are permissible depends on the chosen style. Use
                        the 'showstyleopts' command to find out what is
                        supported for a given template.
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
  -j filename, --inject-metadata filename
                        Gives the option to inject metadata into the
                        presentation. Must point to a JSON filename and will
                        override the respective metadata fields of the
                        presentation. Useful for changing things like the
                        presentation date on the command line.
  -e {interactive,timer,info,pygments,acronyms}, --enable-presentation-feature {interactive,timer,info,pygments,acronyms}
                        Enable a specific presentation feature. Can be one of
                        interactive, timer, info, pygments, acronyms and can
                        be given multiple times.
  -d {interactive,timer,info,pygments,acronyms}, --disable-presentation-feature {interactive,timer,info,pygments,acronyms}
                        Disable a specific presentation feature. Can be one of
                        interactive, timer, info, pygments, acronyms and can
                        be given multiple times.
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
